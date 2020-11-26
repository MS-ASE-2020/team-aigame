using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Runtime.CompilerServices;
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
        private Socket socket;
        private bool watching = false;
        private bool WaitAnimation = false;
        private int count = 0;
        private int seat = -1;
        private int score = 0;
        private int round = 0;
        // record the cards played in one round
        // when count reaches 4, timer is started to keep the cards on the desk and after that, clear


        public PlayPage(bool watcher)
        {
            if (watcher)
                this.watching = true;
            else
                this.watching = false;
            InitializeComponent();
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
                }));
                
            }
        }

        /// <summary>
        /// put one card to the desk (user's card set)
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
            if (direction > 3 || direction < 0)
                return;
            this.Dispatcher.Invoke(new Action(delegate
            {
                UIElementCollection tmp = null;
                switch (direction)
                {
                    case 0: tmp = this.Me.Children; break;
                    case 1: tmp = this.Left.Children; break;
                    case 2: tmp = this.Opponent.Children; break;
                    case 3: tmp = this.Right.Children; break;
                }
                for(int i = 0; i < 13; i++)
                {
                    //if (direction == 1)
                    //{
                    //    RotateTransform rotateTransform = new RotateTransform(90);
                    //    this.CardUI[direction, i].RenderTransform = rotateTransform;
                    //}
                    //else if (direction == 3)
                    //{
                    //    RotateTransform rotateTransform = new RotateTransform(270);
                    //    this.CardUI[direction, i].RenderTransform = rotateTransform;
                    //}
                    if (this.inhand[direction, i])
                    {
                        //tmp.Add(this.CardUI[direction, i]);
                        StackPanel panel = null;
                        for (int j = 0; j < tmp.Count; j++)
                        {
                            StackPanel t = tmp[j] as StackPanel;
                            CardControl c = t.Children[0] as CardControl;
                            if (string.Compare(c.Suit, this.CardUI[direction, i].Suit) == 0)
                            {
                                panel = t;
                                break;
                            }
                        }
                        bool newPanel = false;
                        if (panel == null)
                        {
                            newPanel = true;
                            panel = new StackPanel();
                            panel.Orientation = Orientation.Horizontal;
                            panel.Width = 110;
                            panel.Height = 150;
                            panel.MaxHeight = 150;
                            panel.HorizontalAlignment = HorizontalAlignment.Left;
                        }
                        else
                        {
                            panel.Width += 20;
                        }
                        if (tmp.Count > 0 && newPanel && direction % 2 == 1)
                        {
                            Thickness panelThickness = new Thickness();
                            panelThickness.Top = -107;
                            panel.Margin = panelThickness;
                        }
                        double horizontalOffset = 0;
                        double verticalOffset = 0;
                        if (panel.Children.Count > 0)
                        {
                            horizontalOffset = -80;
                            Thickness thickness = new Thickness();
                            thickness.Left = horizontalOffset;
                            thickness.Top = verticalOffset;
                            this.CardUI[direction, i].Margin = thickness;
                        }
                        this.CardUI[direction, i].MaxHeight = 150;
                        panel.Children.Add(this.CardUI[direction, i]);
                        if(newPanel)
                            tmp.Add(panel);
                    }
                        
                }
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
                UIElementCollection tmp = null;
                UIElementCollection tmp1 = null;
                switch (Convert.ToInt32(card.Owner))
                {
                    case 0: tmp = this.Me.Children; tmp1 = this.MeCard.Children; break;
                    case 1: tmp = this.Left.Children; tmp1 = this.LeftCard.Children; break;
                    case 2: tmp = this.Opponent.Children; tmp1 = this.OpponentCard.Children; break;
                    case 3: tmp = this.Right.Children; tmp1 = this.RightCard.Children; break;
                }
                for(int i = 0; i < tmp.Count; i++)
                {
                    StackPanel t = tmp[i] as StackPanel;
                    for(int j = 0; j < t.Children.Count; j++)
                    {
                        CardControl c = t.Children[j] as CardControl;
                        if (c == card)
                        {
                            t.Children.Remove(card);
                            card.Margin = new Thickness();
                            tmp1.Add(card);
                            t.Width -= 20;
                            if (t.Children.Count == 0)
                            {
                                tmp.Remove(t);
                                if (tmp.Count > 0)
                                {
                                    StackPanel t_ = tmp[0] as StackPanel;
                                    t_.Margin = new Thickness();
                                }
                            }
                            else if(j == 0 && t.Children.Count > 0)
                            {
                                CardControl c_ = t.Children[0] as CardControl;
                                c_.Margin = new Thickness();
                            }
                            break;
                        }
                    }
                }
                //switch (Convert.ToInt32(card.Owner))
                //{
                //    case 0: 
                //        this.Me.Children.Remove(card); 
                //        this.MeCard.Children.Clear(); 
                //        this.MeCard.Children.Add(card); 
                //        break;
                //    case 1: 
                //        this.Left.Children.Remove(card); 
                //        this.LeftCard.Children.Clear(); 
                //        this.LeftCard.Children.Add(card); 
                //        break;
                //    case 2: 
                //        this.Opponent.Children.Remove(card); 
                //        this.OpponentCard.Children.Clear(); 
                //        this.OpponentCard.Children.Add(card); 
                //        break;
                //    case 3: 
                //        this.Right.Children.Remove(card);
                //        this.RightCard.Children.Clear();
                //        this.RightCard.Children.Add(card);
                //        break;
                //    default: 
                //        break;
                //}
            }));
        }

        /// <summary>
        /// <para>clear the card on the desk</para>
        /// <para>used in timer, to make sure the cards will keep on the desk for several seconds after one round is over</para>
        /// </summary>
        private void clearCardInThisTurn()
        {
            this.MeCard.Dispatcher.Invoke(new Action(delegate
            {
                this.MeCard.Children.Clear();
            }));
            this.LeftCard.Dispatcher.Invoke(new Action(delegate
            {
                this.LeftCard.Children.Clear();
            }));
            this.OpponentCard.Dispatcher.Invoke(new Action(delegate
            {
                this.OpponentCard.Children.Clear();
            }));
            this.RightCard.Dispatcher.Invoke(new Action(delegate
            {
                this.RightCard.Children.Clear();
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
                sayHello(this.socket);
                startReceive(this.socket, 1);
            }, null);
        }

        /// <summary>
        /// say hello to the server
        /// </summary>
        private void sayHello(Socket socket)
        {
            Hello h = new Hello();
            if (this.watching)
                h.Code = 1;
            else
                h.Code = 2;
            try
            {
                socket.Send(h.ToByteArray());
            }
            catch (Exception ex)
            {

            }
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
                        if (code == 1)
                        {
                            Hello m = new Hello();
                            m.MergeFrom(receivedData);
                            code = (int)m.Code;
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
                                    this.watcherTimer.Start();
                                    this.scoreLabel.Content = "declarer:0\ndefender:0";
                                }));
                            }
                            sendContinue();
                        }
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
                                    }
                                    else
                                    {
                                        this.tipsLabel.Content = "Your Turn!\nDummy";
                                    }
                                }));
                            }
                        }
                        else if (code == 3)
                        {
                            Play m = new Play();
                            m.MergeFrom(receivedData);
                            int score = (int)m.TableID;
                            this.Dispatcher.Invoke(new Action(delegate
                            {
                                Console.WriteLine("score:{0}", score);
                                this.score = score;
                                this.scoreLabel.Content = "declarer:" + this.score.ToString() + "\ndefender:" + (this.round-this.score).ToString();
                            }));
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
                            this.WaitAnimation = true;
                            if (this.count < 4 && !this.watching)
                            {
                                this.watcherTimer.Interval = 50;
                            }
                            else
                            {
                                this.watcherTimer.Interval = 2000;
                            }
                            this.watcherTimer.Start();
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
            if (this.count == 4)
            {
                clearCardInThisTurn();
                Console.WriteLine("clear card");
                this.count = 0;
                this.round += 1;
            }
            this.watcherTimer.Stop();
            sendContinue();
        }

        protected override void OnInitialized(EventArgs e)
        {
            base.OnInitialized(e);
            for(int i = 0; i < 4; i++)
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
                this.watcherTimer = new System.Timers.Timer(1000);
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
            if(this.watching && this.WaitAnimation)
            {
                this.watcherTimer.Stop();
                this.WaitAnimation = false;
                if (this.count == 4)
                {
                    clearCardInThisTurn();
                    this.count = 0;
                    this.round += 1;
                }
                sendContinue();
            }
        }

    }
}
