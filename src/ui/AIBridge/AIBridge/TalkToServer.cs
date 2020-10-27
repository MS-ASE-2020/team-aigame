using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace AIBridge
{
    class TalkToServer
    {
        private Socket socket;
        private int port;
        public void init(string IP, int port)
        {
            IPAddress ip = IPAddress.Parse(IP); //  server IP
            IPEndPoint point = new IPEndPoint(ip, port);    // server port
            this.socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            try
            {
                this.socket.Connect(point);
            }
            catch
            {
                
            }
        }

        public string receive()
        {
            byte[] buffer = new byte[1024];
            int n = this.socket.BeginReceive(buffer,);
            string s = Encoding.UTF8.GetString(buffer, 0, n);
            return s;
        }

        public void send(string s)
        {
            byte[] buffer = Encoding.UTF8.GetBytes(s);
            this.socket.Send(buffer);
        }
    }
}
