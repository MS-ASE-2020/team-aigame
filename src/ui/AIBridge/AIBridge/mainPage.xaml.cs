using System;
using System.Collections.Generic;
using System.Linq;
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
    /// mainPage.xaml 的交互逻辑
    /// </summary>
    public partial class mainPage : Page
    {
        private WatchSelect WatchSelectPage = null;
        private PlaySelect PlaySelectPage = null;
        public mainPage()
        {
            InitializeComponent();
        }
        private void WATCH_click(object sender, RoutedEventArgs e)
        {
            if (this.WatchSelectPage != null)
            {
                NavigationService.GetNavigationService(this).Navigate(this.WatchSelectPage);
            }
            else
            {
                this.WatchSelectPage = new WatchSelect(this);
                NavigationService.GetNavigationService(this).Navigate(this.WatchSelectPage);
            }
        }
        private void PLAY_click(object sender, RoutedEventArgs e)
        {
            if (this.PlaySelectPage != null)
            {
                NavigationService.GetNavigationService(this).Navigate(this.PlaySelectPage);
            }
            else
            {
                this.PlaySelectPage = new PlaySelect(this);
                NavigationService.GetNavigationService(this).Navigate(this.PlaySelectPage);
            }
        }
    }
}
