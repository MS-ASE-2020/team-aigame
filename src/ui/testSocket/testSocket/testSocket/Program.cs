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

namespace testSocket
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Hello World!");
            Socket socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            Dictionary<string, Socket> dickSocket = new Dictionary<string, Socket>();
            IPAddress ip = IPAddress.Parse("127.0.0.1");
            IPEndPoint ipe = new IPEndPoint(ip, 6006);
            socket.Bind(ipe);
            socket.Listen(2);
            Console.WriteLine("listen to {0}", socket.LocalEndPoint.ToString());
            Socket client = socket.Accept();
            Console.WriteLine("accept {0}", client.RemoteEndPoint.ToString());
            //try
            //{
            while (true)
            {
                Hello m = new Hello();
                m.Seat = Player.Declarer;
                m.Code = 2;
                //MemoryStream ms = new MemoryStream();
                //Serializer.Serialize<Hello>(ms, m);
                Console.WriteLine("send message:{0}", m.ToString());
                byte[] data = m.ToByteArray();//ms.ToArray();
                Console.WriteLine(data);
                client.Send(data);
                Thread.Sleep(1000);
            }
            //}
            //catch(Exception ex)
            //{
            //    Console.WriteLine(ex.ToString());
            //}
        }
    }
}
