using System;
using System.Collections.Generic;
using System.Linq;
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
using System.Windows.Navigation;
using System.Windows.Shapes;

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
        private System.Timers.Timer t = new System.Timers.Timer(3000);
        // record the cards played in one round
        // when count reaches 4, timer is started to keep the cards on the desk and after that, clear
        private int count = 0;
        public int Count
        {
            get { return this.count; }
            set
            {
                this.count = (int)value;
                if((int)value == 4)
                {
                    this.count = 0;
                    this.whooseTurn(-1);
                    t.Start();
                }
                else
                {
                    this.whooseTurn(this.count);
                }
            }
        }


        public PlayPage()
        {
            // here get cards from server
            // todo
            InitializeComponent();
            whooseTurn(0);  // decide the first player
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
                default: return "";
            }
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
            if (encode < 1 || encode > 13)
                return "";
            else if (encode >= 2 && encode <= 10)
                return Convert.ToString(encode);
            else
            {
                switch (encode)
                {
                    case 1: return "A";
                    case 11: return "J";
                    case 12: return "Q";
                    case 13: return "K";
                    default: return "";
                }
            }
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
            this.whooseTurn(0);
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
        private void putCardToDesk(int direction, int index)
        {
            switch (direction)
            {
                case 0: this.Me.Children.Add(this.CardUI[direction, index]); break;
                case 1: this.Left.Children.Add(this.CardUI[direction, index]); break;
                case 2: this.Opponent.Children.Add(this.CardUI[direction, index]); break;
                case 3: this.Right.Children.Add(this.CardUI[direction, index]); break;
                default:break;
            }
        }

        /// <summary>
        /// remove the card from player's hand and put it on the desk
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void selectCard(object sender, RoutedEventArgs e)
        {
            CardControl card = sender as CardControl;
            switch (Convert.ToInt32(card.Owner))
            {
                case 0: this.Me.Children.Remove(card); this.MeCard.Children.Clear(); this.MeCard.Children.Add(card); break;
                case 1: this.Left.Children.Remove(card); this.LeftCard.Children.Clear(); this.LeftCard.Children.Add(card); break;
                case 2: this.Opponent.Children.Remove(card); this.OpponentCard.Children.Clear(); this.OpponentCard.Children.Add(card); break;
                case 3: this.Right.Children.Remove(card); this.RightCard.Children.Clear(); this.RightCard.Children.Add(card); break;
                default: break;
            }

            this.Count += 1;
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

        /// <summary>
        /// decide which player will play next
        /// </summary>
        /// <param name="d">
        /// refers to 4 players, from me, left, opponent, to right (0,1,2,3), -1 refers to disable all players
        /// </param>
        private void whooseTurn(int d)
        {
            int i, j;
            if (d != -1)
            {
                for (i = 0; i < 13; i++)
                {
                    if(this.inhand[d, i])
                    {
                        this.CardUI[d, i].Dispatcher.Invoke(new Action(delegate
                         {
                             this.CardUI[d, i].MouseDoubleClick += selectCard;
                         }));
                    }
                    if(this.inhand[(d+3)%4, i])
                    {
                        this.CardUI[(d + 3) % 4, i].Dispatcher.Invoke(new Action(delegate
                        {
                            this.CardUI[(d + 3) % 4, i].MouseDoubleClick -= selectCard;
                        }));
                    }
                }
            }
            else
            {
                for (i = 0; i < 4; i++)
                    for (j = 0; j < 13; j++)
                        this.CardUI[i, j].Dispatcher.Invoke(new Action(delegate
                        {
                            this.CardUI[i, j].MouseDoubleClick -= selectCard;
                        }));
            }
            
        }

        protected override void OnInitialized(EventArgs e)
        {
            int i, j, k;
            base.OnInitialized(e);
            for (i = 0; i < 4; i++)
            {
                for (j = 0; j < 13; j++)
                {
                    for (k = 0; k < 2; k++)
                    {
                        this.Card[i, j, k] = j + 1;
                    }
                }
            }
            for (i = 0; i < 4; i++)
            {
                for (j = 0; j < 13; j++)
                {
                    if (Card[i, j, 0] == -1 || Card[i, j, 1] == -1)
                        continue;
                    this.CardUI[i, j] = new CardControl();
                    this.CardUI[i, j].Suit = Encode2Suit(Card[i, j, 0]);
                    this.CardUI[i, j].Number = Encode2Number(Card[i, j, 1]);
                    this.CardUI[i, j].Owner = Convert.ToString(i);
                    this.inhand[i, j] = true;
                }
            }
            for (i = 0; i < 4; i++)
            {
                for (j = 0; j < 13; j++)
                {
                    if(this.CardUI[i,j]!=null)
                        putCardToDesk(i, j);
                }
            }
            this.t.Elapsed += new System.Timers.ElapsedEventHandler(time2clearDesk);
            this.t.AutoReset = false;
            this.t.Stop();
        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            NavigationService.GetNavigationService(this).GoBack();
        }
    }
}
