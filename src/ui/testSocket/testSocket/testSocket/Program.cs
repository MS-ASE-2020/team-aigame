using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Runtime.CompilerServices;
using System.Runtime.Serialization.Json;
using System.Text;
using System.Threading;
using System.Runtime.Serialization.Formatters.Binary;
using System.Drawing.Printing;
using Google.Protobuf;
using System.Linq;

namespace testSocket
{
    class Program
    {
        Socket declarerClient = null;
        Socket declarerServer = null;
        Socket loppClient = null;
        Socket loppServer = null;
        Socket roppClient = null;
        Socket roppServer = null;
        Socket watcher = null;
        static void Main(string[] args)
        {
            Console.WriteLine("Hello World!");
            Socket listener = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            IPAddress ip = IPAddress.Parse("127.0.0.1");
            IPEndPoint ipe = new IPEndPoint(ip, 6006);
            listener.Bind(ipe);
            listener.Listen(5);
            Console.WriteLine("listen to {0}", listener.LocalEndPoint.ToString());
            listener.BeginAccept(new AsyncCallback(assignPort), listener);
            Console.WriteLine("ready to accept links");
            while (true)
            {

            }
            //Console.WriteLine("accept {0}", client.RemoteEndPoint.ToString());
            ////try
            ////{
            //while (true)
            //{
            //    Hello m = new Hello();
            //    m.Seat = Player.Declarer;
            //    m.Code = 2;
            //    //MemoryStream ms = new MemoryStream();
            //    //Serializer.Serialize<Hello>(ms, m);
            //    Console.WriteLine("send message:{0}", m.ToString());
            //    byte[] data = m.ToByteArray();//ms.ToArray();
            //    Console.WriteLine(data);
            //    client.Send(data.ToString());
            //    Thread.Sleep(1000);
            //}
            //}
            //catch(Exception ex)
            //{
            //    Console.WriteLine(ex.ToString());
            //}
        }

        public static void assignPort(IAsyncResult ar)
        {
            Socket listener = (Socket)ar.AsyncState;
            Socket client = listener.EndAccept(ar);
            byte[] buffer = new byte[1024];
            int length = client.Receive(buffer);
            byte[] data = buffer.Take(length).ToArray();
            int seat = Convert.ToInt32(data.ToString());
            int newPort = 8000 - seat;
            Socket newSocket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            IPAddress ip = IPAddress.Parse("127.0.0.1");
            IPEndPoint ipe = new IPEndPoint(ip, newPort);
            newSocket.Bind(ipe);
            newSocket.Listen(1);
            newSocket.Accept();

        }
    }
}
