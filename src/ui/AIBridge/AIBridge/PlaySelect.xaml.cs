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
    /// PlaySelect.xaml 的交互逻辑
    /// </summary>
    public partial class PlaySelect : Page
    {
        private mainPage upperPage;
        public PlaySelect(mainPage page)
        {
            InitializeComponent();
            this.upperPage = page;
        }

        private void RuleBase_click(object sender, RoutedEventArgs e)
        {
            currentPage.Content = new PlayPage(false, 10);
        }
        private void SL_click(object sender, RoutedEventArgs e)
        {
            currentPage.Content = new PlayPage(false, 11);
        }
        private void RL_click(object sender, RoutedEventArgs e)
        {
            currentPage.Content = new PlayPage(false, 12);
        }
        private void BACK_click(object sender, RoutedEventArgs e)
        {
            NavigationService.GetNavigationService(this).Navigate(this.upperPage);
        }
    }
}
