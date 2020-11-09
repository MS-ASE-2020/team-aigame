using Google.Protobuf.Collections;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;

namespace AIBridge
{
    class Communicator
    {
        private string _ip = string.Empty;
        private int _port = 0;
        private Socket socket = null;
        private byte[] buffer = new byte[1024];

        public Communicator(string ip, int port)
        {
            this._ip = ip;
            this._port = port;
        }
        public Communicator(int port)
        {
            this._ip = "127.0.0.1";
            this._port = port;
        }

        public void connect()
        {
            try
            {
                this.socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
                IPAddress address = IPAddress.Parse(this._ip);
                IPEndPoint endPoint = new IPEndPoint(address, this._port);
                this.socket.Connect(endPoint);
            }
            catch (Exception ex)
            {
                this.socket.Shutdown(SocketShutdown.Both);
                this.socket.Close();

            }
        }

        public void send(string s)
        {

        }

        public void close()
        {
            this.socket.Shutdown(SocketShutdown.Both);
            this.socket.Close();
        }

        public void receive()
        {

        }
    }
}
