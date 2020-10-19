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
    /// UserControl1.xaml 的交互逻辑
    /// </summary>
    public partial class CardControl : UserControl
    {
        public CardControl()
        {
            InitializeComponent();
        }

        public string Suit
        {
            get { return (string)GetValue(SuitProperty); }
            set { SetValue(SuitProperty, value); }
        }

        // Using a DependencyProperty as the backing store for TextProperty.  This enables animation, styling, binding, etc...
        public static readonly DependencyProperty SuitProperty =
            DependencyProperty.Register("Suit", typeof(string), typeof(CardControl), new PropertyMetadata("", OnSuitChangedCallback));

        private static void OnSuitChangedCallback(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d != null && d is CardControl)
            {
                CardControl cc = d as CardControl;
                cc.tbSuit1.Text = (string)e.NewValue;
                cc.tbSuit2.Text = (string)e.NewValue;
                cc.tbSuit3.Text = (string)e.NewValue;
            }
        }

        public string Number
        {
            get { return (string)GetValue(NumberProperty); }
            set { SetValue(NumberProperty, value); }
        }

        // Using a DependencyProperty as the backing store for NumberProperty.  This enables animation, styling, binding, etc...
        public static readonly DependencyProperty NumberProperty =
            DependencyProperty.Register("Number", typeof(string), typeof(CardControl), new PropertyMetadata("", OnNumberChangedCallback));

        private static void OnNumberChangedCallback(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d != null && d is CardControl)
            {
                CardControl cc = d as CardControl;
                cc.tbNumber1.Text = (string)e.NewValue;
                cc.tbNumber2.Text = (string)e.NewValue;
                cc.tbNumber3.Text = (string)e.NewValue;
            }
        }
    }
}
