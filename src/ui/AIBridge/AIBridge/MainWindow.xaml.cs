using System;
using System.Collections.Generic;
using System.Diagnostics;
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
    /// MainWindow.xaml 的交互逻辑
    /// </summary>
    public partial class MainWindow : Window
    {
        private server s = new server();
        public MainWindow()
        {
            InitializeComponent();
            // todo: deal with the memory problem
            this.MainPage.Content = new mainPage();
            this.Closing += Window_Closing;
            this.s.start();
        }
        private void Window_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            //this.s.stop();
            e.Cancel = false;
        }
    }
}
