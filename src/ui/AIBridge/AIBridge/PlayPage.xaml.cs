using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Runtime.CompilerServices;
using System.ServiceModel.Channels;
using System.ServiceModel.Security;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Media.Imaging;
using System.Windows.Media.TextFormatting;
using System.Windows.Navigation;
using System.Windows.Shapes;
using Google.Protobuf;

namespace AIBridge
{
    /// <summary>
    /// PlayPage.xaml 的交互逻辑
    /// </summary>
    public partial class PlayPage : Page
    {
        /// <summary>
        /// <para>4 x 13 x 2(1 used for suit and another used for number)</para>
        /// <para>for suit dimension</para>
        /// <para>0: club(梅花)</para>
        /// <para>1: diamond(方块)</para>
        /// <para>2: hearts(红桃)</para>
        /// <para>3: spades(黑桃)</para>
        /// <para>-1:no card</para>
        /// <para>for card dimension</para>
        /// <para>0: me</para>
        /// <para>1: left</para>
        /// <para>2: opponent</para>
        /// <para>3: right</para>
        /// </summary>
        public int[,,] Card = new int[4, 13, 2];
        // same definition
        public CardControl[,] CardUI = new CardControl[4, 13];
        public bool[,] inhand = new bool[4, 13];

        // timer for the delay after one round is completed
        private System.Timers.Timer clearTimer = new System.Timers.Timer(3000);
        private System.Timers.Timer watcherTimer = new System.Timers.Timer(2000);
        //private Button ContinueButton;
        //private Button backButton;
        //private Label scoreLabel;
        //private Label tipsLabel;
        //private Label contractLabel;
        private ArrayList outCards = new ArrayList();
        private Socket socket;
        private bool watching = false;
        private bool WaitAnimation = false;
        private bool cardAnimation = false;
        private int count = 0;
        private int seat = -1;
        private int score = 0;
        private int round = 0;
        private bool needClear = false; // tell whether one round is over and need to clear
        private int playerType = 1;
        // record the cards played in one round
        // when count reaches 4, timer is started to keep the cards on the desk and after that, clear


        public PlayPage(bool watcher, int t)
        {
            if (watcher)
                this.watching = true;
            else
                this.watching = false;
            this.playerType = t;
            InitializeComponent();
            System.Timers.Timer tmp = new System.Timers.Timer(50);
            tmp.Elapsed += Tmp_Elapsed;
            tmp.AutoReset = false;
            tmp.Start();
        }

        private void Tmp_Elapsed(object sender, System.Timers.ElapsedEventArgs e)
        {
            this.Dispatcher.Invoke(new Action(delegate
            {
                this.ContinueButton.SetValue(Canvas.LeftProperty, this.canvas.ActualWidth - 10 - this.ContinueButton.ActualWidth);
                this.ContinueButton.SetValue(Canvas.TopProperty, (double)10);

                this.backButton.SetValue(Canvas.LeftProperty, this.canvas.ActualWidth - 10 - this.backButton.ActualWidth);
                this.backButton.SetValue(Canvas.TopProperty, this.canvas.ActualHeight - 10 - this.backButton.ActualHeight);

                this.contractLabel.SetValue(Canvas.LeftProperty, this.canvas.ActualWidth / 2 - this.contractLabel.ActualWidth / 2);
                this.contractLabel.SetValue(Canvas.TopProperty, this.canvas.ActualHeight / 2 - this.contractLabel.ActualHeight / 2);

                this.tipsLabel.SetValue(Canvas.LeftProperty, (double)10);
                this.tipsLabel.SetValue(Canvas.TopProperty, (double)10);

                updateScoreLabel();
            }));
        }


        /// <summary>
        /// from int to suit charactor
        /// </summary>
        /// <param name="encode">
        /// <para>0->club,</para>
        /// <para>1->diamond,</para>
        /// <para>2->hearts,</para>
        /// <para>3->spades,</para>
        /// <para>else->null</para>
        /// </param>
        /// <returns></returns>
        private string Encode2Suit(int encode)
        {
            switch (encode)
            {
                case 0: return "\u2663";
                case 1: return "\u2666";
                case 2: return "\u2665";
                case 3: return "\u2660";
                default: return "x";
            }
        }

        /// <summary>
        /// from suit icons to number
        /// </summary>
        /// <param name="s"></param>
        /// <returns></returns>
        private int Suit2Encode(string s)
        {
            if (string.Compare(s, "\u2663") == 0)
                return 0;
            else if (string.Compare(s, "\u2666") == 0)
                return 1;
            else if (string.Compare(s, "\u2665") == 0)
                return 2;
            else
                return 3;
        }

        /// <summary>
        /// from int to card number ( 2-A)
        /// </summary>
        /// <param name="encode">
        /// the number of card, from 2 to A (1 - 13, 1->A)
        /// </param>
        /// <returns>
        /// string type
        /// </returns>
        private string Encode2Number(int encode)
        {
            if (encode < 0 || encode > 12)
                return "x";
            else if (encode >= 0 && encode <= 8)
                return Convert.ToString(encode+2);
            else
            {
                switch (encode)
                {
                    case 12: return "A";
                    case 9: return "J";
                    case 10: return "Q";
                    case 11: return "K";
                    default: return "x";
                }
            }
        }

        /// <summary>
        /// from number to rank, 0-12 means 2-A
        /// </summary>
        /// <param name="s"></param>
        /// <returns></returns>
        private int Number2Encode(string s)
        {
            if (string.Compare(s, "A") == 0)
                return 12;
            else if (string.Compare(s, "K") == 0)
                return 11;
            else if (string.Compare(s, "Q") == 0)
                return 10;
            else if (string.Compare(s, "J") == 0)
                return 9;
            else
                return Convert.ToInt32(s) - 2;
        }

        /// <summary>
        /// <para>when timer is started, this will be call after a few seconds later,</para>
        /// <para>clear the desk and decide which player will be the first in the next round</para>
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void time2clearDesk(object sender, System.Timers.ElapsedEventArgs e)
        {
            this.clearCardInThisTurn();
        }

        private void updateCardUI(int direction)
        {
            for(int i = 0; i < 13; i++)
            {
                this.Dispatcher.Invoke(new Action(delegate
                {
                    if (this.CardUI[direction, i] == null)
                    {
                        this.CardUI[direction, i] = new CardControl();
                    }
                    if(this.watching || direction==0 || direction == 2)
                    {
                        this.CardUI[direction, i].Suit = Encode2Suit(this.Card[(direction + this.seat) % 4, i, 0]);
                        this.CardUI[direction, i].Number = Encode2Number(this.Card[(direction + this.seat) % 4, i, 1]);
                    }
                    else
                    {
                        this.CardUI[direction, i].Suit = Encode2Suit(-1);
                        this.CardUI[direction, i].Number = Encode2Number(-1);
                    }
                    this.CardUI[direction, i].Owner = direction.ToString();

                    this.CardUI[direction, i].SetValue(Canvas.LeftProperty, this.canvas.ActualWidth / 2 - this.CardUI[direction, i].ActualWidth);
                    this.CardUI[direction, i].SetValue(Canvas.TopProperty, this.canvas.ActualHeight / 2 - this.CardUI[direction, i].ActualHeight);
                    this.canvas.Children.Add(this.CardUI[direction, i]);
                }));
                
            }
        }

        /// <summary>
        /// put one card to the desk (user's card set), call this function only at the beginning of the game
        /// </summary>
        /// <param name="direction">
        /// which user the card belongs to:
        /// <para>0->me</para>
        /// <para>1->left</para>
        /// <para>2->opponent</para>
        /// <para>3->right</para>
        /// </param>
        /// <param name="index">
        /// which card is put, corresponding to the number on the card
        /// </param>
        private void showCardInHand(int direction)
        {
            this.Dispatcher.Invoke(new Action(delegate
            {
                int[] card_count = { 0, 0, 0, 0 };
                double[,] dest = new double[13, 2]; // 13 x (left, top)
                for(int i = 0; i < 13; i++)
                {
                    if(this.inhand[direction, i])
                    {
                        card_count[this.Card[direction, i, 0]] += 1;
                    }
                }
                double height = 0;
                double width = 0;
                int suit_count = 0;
                int card_num = 0;
                double left = 0;
                double top = 0;
                int maxNumberOfCard = -1;
                for(int i = 0; i < 4; i++)
                {
                    if (card_count[i] > 0)
                    {
                        suit_count += 1;
                    }
                    if (card_count[i] > maxNumberOfCard)
                    {
                        maxNumberOfCard = card_count[i];
                    }
                    card_num += card_count[i];
                }
                if(direction == 0 || direction == 2)
                {
                    height = 150;
                    width = 20 * card_num + (suit_count - 1) * 90 + 80;
                    left = this.canvas.ActualWidth / 2 - width / 2;
                    if (direction == 0)
                        top = this.canvas.ActualHeight - 160;
                    else
                        top = 10;
                    int lastSuit = -1;
                    for (int i = 0; i < 13; i++)
                    {
                        if(this.inhand[direction, i])
                        {
                            if (this.Card[direction, i, 0] != lastSuit && lastSuit != -1)
                            {
                                left += 90;
                            }
                            dest[i, 0] = left;
                            dest[i, 1] = top;
                            lastSuit = this.Card[direction, i, 0];
                            //this.CardUI[direction, i].SetValue(Canvas.LeftProperty, left);
                            //this.CardUI[direction, i].SetValue(Canvas.TopProperty, top);
                            //this.canvas.Children.Add(this.CardUI[direction, i]);
                            left += 20;
                        }
                    }
                }
                else
                {
                    if (this.watching)
                    {
                        height = 43 * suit_count + 107;
                        width = 20 * maxNumberOfCard + 90;
                        int lastSuit = -1;
                        top = this.canvas.ActualHeight / 2 - height / 2;
                        if (direction == 1)
                            left = 10;
                        else
                            left = this.canvas.ActualWidth - width;
                        double raw_left = left;
                        for(int i = 0; i < 13; i++)
                        {
                            if(this.inhand[direction, i])
                            {
                                if (this.Card[direction, i, 0] != lastSuit && lastSuit != -1)
                                {
                                    left = raw_left;
                                    top += 43;
                                }
                                dest[i, 0] = left;
                                dest[i, 1] = top;
                                lastSuit = this.Card[direction, i, 0];
                                //this.CardUI[direction, i].SetValue(Canvas.LeftProperty, left);
                                //this.CardUI[direction, i].SetValue(Canvas.TopProperty, top);
                                //this.canvas.Children.Add(this.CardUI[direction, i]);
                                left += 20;
                            }
                        }
                    }
                    else
                    {
                        height = 43 * card_num + 107;
                        width = 100;
                        if (direction == 1)
                            left = 10;
                        else
                            left = this.canvas.ActualWidth - 10 - width;
                        top = this.canvas.ActualHeight / 2 - height / 2;
                        for (int i = 0; i < 13; i++)
                        {
                            if(this.inhand[direction, i])
                            {
                                dest[i, 0] = left;
                                dest[i, 1] = top;
                                //this.CardUI[direction, i].SetValue(Canvas.LeftProperty, left);
                                //this.CardUI[direction, i].SetValue(Canvas.TopProperty, top);
                                //this.canvas.Children.Add(this.CardUI[direction, i]);
                                top += 43;
                            }
                        }
                    }
                }
                Storyboard s = new Storyboard();
                for(int i = 0; i < 13; i++)
                {
                    if(this.inhand[direction, i])
                    {
                        DoubleAnimation da1 = new DoubleAnimation(Canvas.GetLeft(this.CardUI[direction, i]), dest[i, 0], new Duration(TimeSpan.FromMilliseconds(500)));
                        Storyboard.SetTarget(da1, this.CardUI[direction, i]);
                        Storyboard.SetTargetProperty(da1, new PropertyPath("(Canvas.Left)"));
                        s.Children.Add(da1);

                        DoubleAnimation da2 = new DoubleAnimation(Canvas.GetTop(this.CardUI[direction, i]), dest[i, 1], new Duration(TimeSpan.FromMilliseconds(500)));
                        Storyboard.SetTarget(da2, this.CardUI[direction, i]);
                        Storyboard.SetTargetProperty(da2, new PropertyPath("(Canvas.Top)"));
                        s.Children.Add(da2);
                    }
                }
                s.Begin();
            }));
            
        }

        /// <summary>
        /// remove the card from player's hand and put it on the desk
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void selectCard(object sender, RoutedEventArgs e)
        {
            CardControl card = (CardControl)sender;
            this.Dispatcher.Invoke(new Action(delegate
            {
                this.tipsLabel.Content = "";
                card.MouseDoubleClick -= selectCard;
                Play m = new Play();
                m.Who = (Player)Convert.ToInt32(card.Owner);
                Card c = new Card();
                c.Suit = (Suit)Suit2Encode(card.Suit);
                c.Rank = (uint)Number2Encode(card.Number);
                m.Card = c;
                try
                {
                    this.socket.Send(m.ToByteArray());
                }
                catch (Exception ex)
                {

                }
                this.ContinueButton.Click += Button_Click_1;
                for(int i = 0; i < 13; i++)
                {
                    this.CardUI[Convert.ToInt32(card.Owner), i].MouseDoubleClick -= selectCard;
                }
            }));
        }

        private void cardOut(CardControl card)
        {
            this.Dispatcher.Invoke(new Action(delegate
            {
                int direction = Convert.ToInt32(card.Owner);
                double left = 0;
                double top = 0;
                switch (direction)
                {
                    case 0: left = Canvas.GetLeft(this.contractLabel) + this.contractLabel.ActualWidth/2 - 50; top = Canvas.GetTop(this.contractLabel) + this.contractLabel.ActualHeight + 10; break;
                    case 1: left = Canvas.GetLeft(this.contractLabel) - 110; top = Canvas.GetTop(this.contractLabel) + this.contractLabel.ActualHeight / 2 - 75; break;
                    case 2: left = Canvas.GetLeft(this.contractLabel) + this.contractLabel.ActualWidth / 2 - 50; top = Canvas.GetTop(this.contractLabel) - 160; break;
                    case 3: left = Canvas.GetLeft(this.contractLabel) + this.contractLabel.ActualWidth + 10; top = Canvas.GetTop(this.contractLabel) + this.contractLabel.ActualHeight / 2 - 75; break;
                }
                Storyboard s = new Storyboard();
                DoubleAnimation da1 = new DoubleAnimation(Canvas.GetLeft(card), left, new Duration(TimeSpan.FromMilliseconds(500)));
                Storyboard.SetTarget(da1, card);
                Storyboard.SetTargetProperty(da1, new PropertyPath("(Canvas.Left)"));
                s.Children.Add(da1);

                DoubleAnimation da2 = new DoubleAnimation(Canvas.GetTop(card), top, new Duration(TimeSpan.FromMilliseconds(500)));
                Storyboard.SetTarget(da2, card);
                Storyboard.SetTargetProperty(da2, new PropertyPath("(Canvas.Top)"));
                s.Children.Add(da2);

                this.outCards.Add(card);

                s.Begin();
                showCardInHand(direction);
            }));
        }

        /// <summary>
        /// <para>clear the card on the desk</para>
        /// <para>used in timer, to make sure the cards will keep on the desk for several seconds after one round is over</para>
        /// </summary>
        private void clearCardInThisTurn()
        {
            this.Dispatcher.Invoke(new Action(delegate
            {
                for(int i = 0; i < this.outCards.Count; i++)
                {
                    CardControl c = this.outCards[i] as CardControl;
                    this.canvas.Children.Remove(c);
                }
                this.outCards.Clear();
            }));
        }

        private void sendPlay(object sender, RoutedEventArgs e)
        {
            this.Dispatcher.Invoke(new Action(delegate
            {
                CardControl card = sender as CardControl;
                UserEnable(Convert.ToInt32(card.Owner), false);
                Play m = new Play();
                m.Who = (Player)this.seat;
                Card c = new Card();
                c.Suit = (Suit)Convert.ToInt32(card.Suit);
                c.Rank = (uint)Convert.ToInt32(card.Number);
                m.Card = c;
                try
                {
                    this.socket.Send(m.ToByteArray());
                }
                catch(Exception ex)
                {

                }
            }));


        }

        /// <summary>
        /// enable or disable card doubleclick event
        /// </summary>
        /// <param name="d">
        /// refers to 4 players, from me, left, opponent, to right (0,1,2,3), -1 refers to disable all players
        /// </param>
        /// <param name="enable">
        /// enable or not
        /// </param>
        private void UserEnable(int d, bool enable)
        {
            int i;
            for (i = 0; i < 13; i++)
            {
                if(this.inhand[d, i])
                {
                    if (enable)
                    {
                        this.CardUI[d, i].Dispatcher.Invoke(new Action(delegate
                            {
                                this.CardUI[d, i].MouseDoubleClick += sendPlay;
                            }));
                    }
                    else
                    {
                        this.CardUI[d, i].Dispatcher.Invoke(new Action(delegate
                            {
                                this.CardUI[d, i].MouseDoubleClick -= sendPlay;
                            }));
                    }
                }
            }           
        }

        /// <summary>
        /// connect to server and say hello. start to listen to the information from server
        /// </summary>
        private void startConnection()
        {
            this.socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            IPAddress ip = IPAddress.Parse("127.0.0.1");
            IPEndPoint ipe = new IPEndPoint(ip, 6006);
            this.socket.BeginConnect(ipe, asyncResult =>
            {
                this.socket.EndConnect(asyncResult);

                Console.WriteLine("connect to {0}", this.socket.RemoteEndPoint.ToString());
                byte[] buffer = new byte[1024];
                int length = this.socket.Receive(buffer);
                sayHello(this.socket, 4);
                sayHello(this.socket, this.playerType);
                startReceive(this.socket, 1);
            }, null);
        }


        /// <summary>
        /// say hello to the server
        /// </summary>
        private void sayHello(Socket socket, int code)
        {
            Hello h = new Hello();
            h.Code = (uint)code;
            try
            {
                socket.Send(h.ToByteArray());
            }
            catch (Exception ex)
            {

            }
        }

        private void updateScoreLabel()
        {
            this.declarerScoreLabel.Content = "declarer:" + this.score.ToString();
            this.defenderScoreLabel.Content = "defender:" + (this.round - this.score).ToString();
            this.defenderScoreLabel.SetValue(Canvas.LeftProperty, (double)10);
            this.defenderScoreLabel.SetValue(Canvas.TopProperty, this.canvas.ActualHeight - 10 - this.defenderScoreLabel.ActualHeight);
            this.declarerScoreLabel.SetValue(Canvas.LeftProperty, (double)10);
            this.declarerScoreLabel.SetValue(Canvas.TopProperty, this.canvas.ActualHeight - 10 - this.defenderScoreLabel.ActualHeight - this.declarerScoreLabel.ActualHeight);
        }


        /// <summary>
        /// async receive data from server
        /// </summary>
        /// <param name="socket"></param>
        private void startReceive(Socket socket, int code)
        {
            byte[] data = new byte[1024];
            try
            {
                socket.BeginReceive(data, 0, data.Length, SocketFlags.None, asyncResult =>
                {
                    try
                    {
                        int length = socket.EndReceive(asyncResult);
                        Console.WriteLine("{0} bytes received", length);
                        byte[] receivedData = data.Take(length).ToArray();
                        // inform ui what next information will be
                        if (code == 1)
                        {
                            Hello m = new Hello();
                            m.MergeFrom(receivedData);
                            code = (int)m.Code;
                            // if received hello with code 4, means cards are distributed successfully. update ui then
                            if (code == 4)
                            {
                                this.seat = 0;
                                Console.WriteLine("card updated");
                                for (int i = 0; i < 4; i++)
                                {
                                    updateCardUI(i);    // update all
                                }
                                for (int i = 0; i < 4; i++)
                                {
                                    showCardInHand(i);
                                }
                                code = 1;
                                this.Dispatcher.Invoke(new Action(delegate
                                {
                                    this.WaitAnimation = true;
                                    if (!this.watching)
                                    {
                                        this.watcherTimer.Start();  // when playing with models, start watcherTimer, to send continue message automatically
                                    }
                                    this.score = 0; // reset score
                                    this.round = 0; // reset round
                                    updateScoreLabel();
                                }));
                            }
                            sendContinue();
                        }
                        // receive gamestate
                        // ui will receive this only when the watcher is not playing, i.e. is watching, or at the beginning of a game when watching
                        else if (code == 2)
                        {
                            GameState m = new GameState();
                            m.MergeFrom(receivedData);
                            code = 1;
                            int who = (int)m.Who;
                            int toplay = (int)m.TableID;
                            if (toplay == 0)
                            {
                                for (int i = 0; i < 13; i++)
                                {
                                    if (i < m.Hand.Count)
                                    {
                                        this.Card[who, i, 0] = (int)m.Hand[i].Suit;
                                        this.Card[who, i, 1] = (int)m.Hand[i].Rank;
                                        this.inhand[who, i] = true;
                                    }
                                    else
                                    {
                                        this.Card[who, i, 0] = -1;
                                        this.Card[who, i, 1] = -1;
                                        this.inhand[who, i] = false;
                                    }
                                }
                                Console.WriteLine("{0} card received", who);
                                sendContinue();
                            }
                            else
                            {
                                for (int i = 0; i < 13; i++)
                                {
                                    for (int j = 0; j < m.ValidPlays.Count; j++)
                                    {
                                        if (this.Card[who, i, 0] == (int)m.ValidPlays[j].Suit && this.Card[who, i, 1] == (int)m.ValidPlays[j].Rank)
                                        {
                                            this.Dispatcher.Invoke(new Action(delegate
                                            {
                                                this.CardUI[who, i].MouseDoubleClick += selectCard;
                                            }));
                                            break;
                                        }
                                    }
                                }
                                this.Dispatcher.Invoke(new Action(delegate
                                {
                                    this.ContinueButton.Click -= Button_Click_1;
                                    if (who == 0)
                                    {
                                        this.tipsLabel.Content = "Your Turn!\nDeclarer";
                                        this.tipsLabel.SetValue(Canvas.LeftProperty, (double)10);
                                        this.tipsLabel.SetValue(Canvas.TopProperty, (double)10);
                                    }
                                    else
                                    {
                                        this.tipsLabel.Content = "Your Turn!\nDummy";
                                    }
                                }));
                            }
                        }
                        // receive play message
                        // add count -> when count reaches 4, means 1 round is over, clear desk
                        // when watching, once a round is over, do not use watcher timer to continue but use continue button only. in other cases, just set the watchertimer to 2s
                        // when playing(!watching), once a round is over, keep the desk for a while(2s or 3s). in other cases, set the watcher to 500ms
                        else if (code == 3)
                        {
                            Play m = new Play();
                            m.MergeFrom(receivedData);
                            this.count += 1;

                            code = 1;
                            int who = (int)m.Who;
                            Card card = m.Card;
                            CardControl sc = null;
                            for (int i = 0; i < 13; i++)
                            {
                                if (this.Card[who, i, 0] == (int)card.Suit && this.Card[who, i, 1] == (int)card.Rank)
                                {
                                    sc = this.CardUI[(4 + who - this.seat) % 4, i];
                                    this.Dispatcher.Invoke(new Action(delegate
                                    {
                                        sc.Suit = Encode2Suit(this.Card[who, i, 0]);
                                        sc.Number = Encode2Number(this.Card[who, i, 1]);
                                    }));
                                    this.inhand[who, i] = false;
                                    cardOut(sc);
                                    break;
                                }
                            }
                            if (this.count == 4)
                            {
                                this.count = 0;
                                this.round += 1;
                                this.needClear = true;
                            }
                            // when there will be button
                            // when only watching, there will always be a button
                            // when playing, only when 13 rounds is finished, there will be a continue button
                            if(this.watching || this.round == 13)
                            {
                                this.WaitAnimation = true;
                                this.Dispatcher.Invoke(new Action(delegate
                                {
                                    this.ContinueButton.Visibility = Visibility.Visible;
                                }));
                            }
                            if (!this.needClear)
                            {
                                if (this.watching)
                                    this.watcherTimer.Interval = 2000;
                                else
                                    this.watcherTimer.Interval = 500;
                                this.watcherTimer.Start();
                            }
                            else if(!this.watching && this.needClear && this.round < 13)
                            {
                                this.watcherTimer.Interval = 2000;
                                this.watcherTimer.Start();
                            }

                            int score = (int)m.Score;
                            this.Dispatcher.Invoke(new Action(delegate
                            {
                                Console.WriteLine("score:{0}", score);
                                this.score = score;
                                updateScoreLabel();
                            }));
                        }
                        else if (code == 5)
                        {
                            Console.WriteLine("received restart ok signal");
                            code = 1;
                        }
                        startReceive(socket, code);
                    }
                    catch (Exception ex)
                    {

                    }
                    
                }, null);
            }
            catch (Exception ex)
            {

            }
        }

        /// <summary>
        /// send message to server
        /// </summary>
        /// <param name="socket"></param>
        /// <param name="message"></param>
        private void sendContinue()
        {
            Hello m = new Hello();
            m.Code = 1;
            try
            {
                this.socket.Send(m.ToByteArray());
            }
            catch(Exception ex)
            {

            }
        }


        private void time2nextPlay(object sender, System.Timers.ElapsedEventArgs e)
        {
            Console.Write("timer elapsed, count:{0}", this.count);
            this.WaitAnimation = false;
            if (this.needClear)
            {
                clearCardInThisTurn();
                Console.WriteLine("clear card");
                this.needClear = false;
            }
            if (!this.watching)
            {
                this.Dispatcher.Invoke(new Action(delegate
                {
                    this.ContinueButton.Visibility = Visibility.Hidden;
                }));
            }
            this.watcherTimer.Stop();
            sendContinue();
        }

        protected override void OnInitialized(EventArgs e)
        {
            base.OnInitialized(e);

            //this.ContinueButton = new Button();
            //this.ContinueButton.Content = "continue";
            //this.ContinueButton.Click += Button_Click_1;
            //this.ContinueButton.FontSize = 30;
            //this.canvas.Children.Add(this.ContinueButton);

            //this.backButton = new Button();
            //this.backButton.Content = "BACK";
            //this.backButton.Click += Button_Click;
            //this.backButton.FontSize = 40;
            //this.canvas.Children.Add(this.backButton);

            //this.contractLabel = new Label();
            //this.contractLabel.Content = "no trump\n   3   ";
            //this.contractLabel.VerticalAlignment = VerticalAlignment.Center;
            //this.contractLabel.HorizontalContentAlignment = HorizontalAlignment.Center;
            //this.contractLabel.FontSize = 20;
            //this.contractLabel.Foreground = new SolidColorBrush(Colors.White);
            //this.canvas.Children.Add(this.contractLabel);

            //this.tipsLabel = new Label();
            //this.tipsLabel.FontSize = 30;
            //this.tipsLabel.Foreground = new SolidColorBrush(Colors.White);
            //this.canvas.Children.Add(this.tipsLabel);

            //this.scoreLabel = new Label();
            //this.scoreLabel.FontSize = 20;
            //this.scoreLabel.HorizontalContentAlignment = HorizontalAlignment.Center;
            //this.scoreLabel.VerticalAlignment = VerticalAlignment.Center;
            //this.scoreLabel.Foreground = new SolidColorBrush(Colors.White);
            //this.canvas.Children.Add(this.scoreLabel);
            //UpdateLayout();


            UpdateLayout();

            for (int i = 0; i < 4; i++)
            {
                for(int j = 0; j < 13; j++)
                {
                    for(int k = 0; k < 2; k++)
                    {
                        this.Card[i, j, k] = -1;
                    }
                }
            }
            if (!this.watching)
            {
                this.clearTimer.Elapsed += new System.Timers.ElapsedEventHandler(time2clearDesk);
                this.clearTimer.AutoReset = false;
                this.clearTimer.Stop();
            }
            //else
            //{
            if (!this.watching)
            {
                this.watcherTimer = new System.Timers.Timer(500);
            }
            else
            {
                this.watcherTimer = new System.Timers.Timer(2000);
            }
            
            this.watcherTimer.Elapsed += new System.Timers.ElapsedEventHandler(time2nextPlay);
            this.watcherTimer.AutoReset = false;
            this.watcherTimer.Stop();
            //}
            if (!this.watching)
            {
                this.ContinueButton.Visibility = Visibility.Hidden;
            }
            startConnection();
        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            this.socket.Shutdown(SocketShutdown.Both);
            this.socket.Close();
            NavigationService.GetNavigationService(this).GoBack();
        }

        private void Page_KeyDown(object sender, KeyEventArgs e)
        {
            Console.WriteLine("keydown captured");
            
        }

        private void Button_Click_1(object sender, RoutedEventArgs e)
        {
            if(this.WaitAnimation)
            {
                this.watcherTimer.Stop();
                this.WaitAnimation = false;
                if (this.needClear)
                {
                    clearCardInThisTurn();
                    this.needClear = false;
                }
                if (!this.watching)
                {
                    this.Dispatcher.Invoke(new Action(delegate
                    {
                        this.ContinueButton.Visibility = Visibility.Hidden;
                    }));
                }
                sendContinue();
            }
        }

    }
}
