using System;
using System.Collections.Generic;
using System.Data;
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
    /// AIselect.xaml 的交互逻辑
    /// </summary>
    public partial class AIselect : Page
    {
        private mainPage upperPage;
        public AIselect(mainPage page)
        {
            InitializeComponent();
            this.upperPage = page;
        }
        private void EASY_click(object sender, RoutedEventArgs e)
        {
            currentPage.Content = new PlayPage(false);
        }

        private void MID_click(object sender, RoutedEventArgs e)
        {
            currentPage.Content = new PlayPage(true);
        }
        private void HARD_click(object sender, RoutedEventArgs e)
        {
            currentPage.Content = new PlayPage(true);
        }

        private void BACK_click(object sender, RoutedEventArgs e)
        {
            NavigationService.GetNavigationService(this).Navigate(this.upperPage);
            
        }
    }
}
