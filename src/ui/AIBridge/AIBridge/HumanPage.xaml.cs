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
    /// HumanPage.xaml 的交互逻辑
    /// </summary>
    public partial class HumanPage : Page
    {
        public HumanPage()
        {
            InitializeComponent();
        }

        private void join_click(object sender, RoutedEventArgs e)
        {
            
        }

        private void invite_click(object sender, RoutedEventArgs e)
        {
            
        }

        private void BACK_click(object sender, RoutedEventArgs e)
        {
            currentPage.Content = new mainPage();
        }
    }
}
