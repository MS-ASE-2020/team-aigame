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
        private AIselect aIselect = null;
        private HumanPage humanPage = null;
        private settingPage SettingPage = null;
        public mainPage()
        {
            InitializeComponent();
        }
        private void AI_click(object sender, RoutedEventArgs e)
        {
            if (this.aIselect != null)
            {
                NavigationService.GetNavigationService(this).Navigate(this.aIselect);
            }
            else
            {
                this.aIselect = new AIselect(this);
                NavigationService.GetNavigationService(this).Navigate(this.aIselect);
            }
        }
        private void Human_click(object sender, RoutedEventArgs e)
        {
            if (this.humanPage != null)
            {
                NavigationService.GetNavigationService(this).Navigate(this.humanPage);
            }
            else
            {
                this.humanPage = new HumanPage(this);
                NavigationService.GetNavigationService(this).Navigate(this.humanPage);
            }
        }
        private void Setting_click(object sender, RoutedEventArgs e)
        {
            if (this.SettingPage != null)
            {
                NavigationService.GetNavigationService(this).Navigate(this.SettingPage);
            }
            else
            {
                this.SettingPage = new settingPage();
                NavigationService.GetNavigationService(this).Navigate(this.SettingPage);
            }
        }
    }
}
