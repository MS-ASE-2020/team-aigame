using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
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
    /// WatchSelect.xaml 的交互逻辑
    /// </summary>
    public partial class WatchSelect : Page
    {
        private mainPage upperPage;
        private string icon = "\u21D2";
        private int declarer = 0; // 0 -> rule based, 1 -> sl, 2 -> rl
        private int defender = 0;
        
        private void updateLabel()
        {
            this.rule1.Content = "   Rule base";
            this.rule2.Content = "   Rule base";
            this.sl1.Content = "   SL model";
            this.sl2.Content = "   SL model";
            this.rl1.Content = "   RL model";
            this.rl2.Content = "   RL model";
            switch (this.declarer)
            {
                case 0: this.rule1.Content = this.icon + "Rule base"; break;
                case 1: this.sl1.Content = this.icon + "SL model"; break;
                case 2: this.rl1.Content = this.icon + "RL model"; break;
            }
            switch (this.defender)
            {
                case 0: this.rule2.Content = this.icon + "Rule base"; break;
                case 1: this.sl2.Content = this.icon + "SL model"; break;
                case 2: this.rl2.Content = this.icon + "RL model"; break;
            }
        }

        public WatchSelect(mainPage page)
        {
            InitializeComponent();
            this.upperPage = page;
        }
        private void BACK_click(object sender, RoutedEventArgs e)
        {
            NavigationService.GetNavigationService(this).Navigate(this.upperPage);
        }
        private void START_click(object sender, RoutedEventArgs e)
        {
            int code = 0;
            if(this.declarer==0)
            {
                if (this.defender == 0)
                {
                    code = 1;
                }
                else if (this.defender == 1)
                {
                    code = 4;
                }
                else
                {
                    code = 6;
                }
            }
            else if (this.declarer == 1)
            {
                if (this.defender == 0)
                {
                    code = 5;
                }
                else if (this.defender == 1)
                {
                    code = 2;
                }
                else
                {
                    code = 8;
                }
            }
            else
            {
                if (this.defender == 0)
                {
                    code = 7;
                }
                else if (this.defender == 1)
                {
                    code = 9;
                }
                else
                {
                    code = 3;
                }
            }
            this.currentPage.Content = new PlayPage(true, code);
        }

        private void Select_click(object sender, RoutedEventArgs e)
        {
            Label label = sender as Label;
            if (label == this.rule1)
            {
                this.declarer = 0;
            }
            else if(label == this.sl1)
            {
                this.declarer = 1;
            }
            else if(label == this.rl1)
            {
                this.declarer = 2;
            }
            else if(label == this.rule2)
            {
                this.defender = 0;
            }
            else if (label == this.sl2)
            {
                this.defender = 1;
            }
            else if(label == this.rl2)
            {
                this.defender = 2;
            }
            updateLabel();
        }

        protected override void OnInitialized(EventArgs e)
        {
            base.OnInitialized(e);
            updateLabel();
        }

    }
}
