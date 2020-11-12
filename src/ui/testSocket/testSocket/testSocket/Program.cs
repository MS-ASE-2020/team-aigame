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
using System.Collections;

namespace testSocket
{
    class Program
    {
        static void Main(string[] args)
        {
            Socket declarer = null;
            Socket lopp = null;
            Socket ropp = null;
            Socket watcher = null;
            byte[] buffer = new byte[1024];
            Console.WriteLine("game started!");
            Socket listener = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            IPAddress ip = IPAddress.Parse("127.0.0.1");
            IPEndPoint ipe = new IPEndPoint(ip, 6006);
            listener.Bind(ipe);
            listener.Listen(4);
            Console.WriteLine("listen to {0}", listener.LocalEndPoint.ToString());
            for(int i = 0; i < 3; i++)
            {
                Socket tmp = listener.Accept();
                Hello m = new Hello();
                if (i != 2)
                    m.Seat = (Player)i;
                else
                    m.Seat = (Player)(i + 1);
                tmp.Send(m.ToByteArray());
                switch (i)
                {
                    case 0: declarer = tmp; Console.WriteLine("declarer connected"); break;
                    case 1: lopp = tmp; Console.WriteLine("lopp connected"); break;
                    case 2: ropp = tmp; Console.WriteLine("ropp connected"); break;
                }
            }
            watcher = listener.Accept();
            Console.WriteLine("watcher connected!");
            int[] card = getRandomCard(52);
            int[] declarerCard = card.Take(13).ToArray();
            Array.Sort(declarerCard);
            int[] loppCard = card.Skip(13).Take(13).ToArray();
            Array.Sort(loppCard);
            int[] dummyCard = card.Skip(26).Take(13).ToArray();
            Array.Sort(dummyCard);
            int[] roppCard = card.Skip(39).Take(13).ToArray();
            Array.Sort(roppCard);
            Console.WriteLine("card distributed!");
            for(int i = 0; i < 3; i++)
            {
                Socket tmp = null;
                int[] tmpCard = null;
                switch (i)
                {
                    case 0: tmp = declarer; tmpCard = declarerCard;  break;
                    case 1: tmp = lopp; tmpCard = loppCard; break;
                    case 2: tmp = ropp; tmpCard = roppCard; break;
                }

            }
            int starter = 0;
            int presentSuit = -1;

            for(int round = 0; round < 13; round++)
            {

            }
            //listener.BeginAccept(new AsyncCallback(assignPort), listener);
            //Console.WriteLine("ready to accept links");
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

        private static int[] getRandomCard(int length)
        {
            int[] nums = new int[length];
            for(int i = 0; i < length; i++)
            {
                nums[i] = i;
            }
            for(int i = 0; i < length; i++)
            {
                Random random = new Random();
                int tmp = nums[i];
                int r = random.Next(i, nums.Length);
                nums[i] = nums[r];
                nums[r] = tmp;
            }
            return nums;
        }

        private static void printCard(int[] card)
        {
            for(int i = 0; i < card.Length; i++)
            {
                if (card[i] != 0)
                {
                    Console.Write("{0},{1}\t", card[i] / 13, card[i] % 13);
                }
            }
            Console.Write("\n");
        }

        private static GameState GetGameState(int who, int[] hand, int[] dummy, ArrayList history)
        {
            GameState state = new GameState();

        }
    }
}
