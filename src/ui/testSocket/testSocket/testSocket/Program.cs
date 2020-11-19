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
            Socket listener = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            IPAddress ip = IPAddress.Parse("127.0.0.1");
            IPEndPoint ipe = new IPEndPoint(ip, 6006);
            byte[] buffer = new byte[1024];
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
                m.Code = 1;
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
            Hello h = new Hello();
            int length = watcher.Receive(buffer);
            h.MergeFrom(buffer.Take(length).ToArray());
            if (h.Code == 2)
            {
                Console.WriteLine("watcher in the game");
                declarer = watcher;
            }
            try
            {
                while (true)
                {
                    run(declarer, lopp, ropp, watcher);
                    h.Code = 5;
                    watcher.Send(h.ToByteArray());
                    watcher.Receive(buffer);
                    watcher.Send(h.ToByteArray());
                    watcher.Receive(buffer);
                }
            }
            catch(Exception ex)
            {
                Console.WriteLine(ex);
                Console.ReadKey();

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

        private static void run(Socket declarer, Socket lopp, Socket ropp, Socket watcher)
        {
            byte[] buffer = new byte[1024];
            Console.WriteLine("game started!");
            int[] card = getRandomCard(52);
            int[] declarerCard = card.Take(13).ToArray();
            Array.Sort(declarerCard);
            printCard(declarerCard);
            int[] loppCard = card.Skip(13).Take(13).ToArray();
            Array.Sort(loppCard);
            printCard(loppCard);
            int[] dummyCard = card.Skip(26).Take(13).ToArray();
            Array.Sort(dummyCard);
            printCard(dummyCard);
            int[] roppCard = card.Skip(39).Take(13).ToArray();
            Array.Sort(roppCard);
            printCard(roppCard);
            Console.WriteLine("card distributed!");
            int starter = 1;
            int presentSuit = -1;
            int score = 0;
            ArrayList history = new ArrayList();
            Hello h = new Hello();
            for (int i = 0; i < 4; i++)
            {
                int[] tmpCard = null;
                switch (i)
                {
                    case 0: tmpCard = declarerCard; break;
                    case 1: tmpCard = loppCard; break;
                    case 2: tmpCard = declarerCard; break;
                    case 3: tmpCard = roppCard; break;
                }
                h.Code = 2;
                watcher.Send(h.ToByteArray());
                watcher.Receive(buffer);
                GameState m = GetGameState(i, tmpCard, dummyCard, history);
                watcher.Send(m.ToByteArray());
                Console.WriteLine("send {0}", i);
                watcher.Receive(buffer);
            }
            h.Code = 4;
            watcher.Send(h.ToByteArray());
            Console.WriteLine("send update message");
            watcher.Receive(buffer);
            Console.WriteLine("start game");

            for (int round = 0; round < 13; round++)
            {
                int[] cardInThisTurn = new int[4];
                for (int p = 0; p < 4; p++)
                {
                    watcher.Receive(buffer);
                    Socket tmpSocket = null;
                    int[] tmpCard = null;
                    switch ((starter + p) % 4)
                    {
                        case 0: tmpSocket = declarer; tmpCard = declarerCard; break;
                        case 1: tmpSocket = lopp; tmpCard = loppCard; break;
                        case 2: tmpSocket = declarer; tmpCard = declarerCard; break;
                        case 3: tmpSocket = ropp; tmpCard = roppCard; break;
                    }
                    GameState m = GetGameState((starter + p) % 4, tmpCard, dummyCard, history);
                    m.TableID = 1;
                    if(tmpSocket==declarer && declarer == watcher)
                    {
                        h.Code = 2;
                        tmpSocket.Send(h.ToByteArray());
                        tmpSocket.Receive(buffer);
                    }
                    tmpSocket.Send(m.ToByteArray());
                    Console.WriteLine("send message to {0}", (starter + p) % 4);
                    int length = tmpSocket.Receive(buffer);
                    Console.WriteLine("receive message from {0}", (starter + p) % 4);
                    Play rm = new Play();
                    rm.MergeFrom(buffer.Take(length).ToArray());
                    rm.TableID = (uint)score;
                    h.Code = 3;
                    watcher.Send(h.ToByteArray());
                    watcher.Receive(buffer);
                    watcher.Send(rm.ToByteArray());
                    Console.WriteLine("send play message");

                    Card selected = rm.Card;
                    if ((starter + p) % 4 == 2)
                        tmpCard = dummyCard;
                    for (int i = 0; i < 13; i++)
                    {
                        if (tmpCard[i] == ((int)selected.Suit * 13 + (int)selected.Rank))
                        {
                            tmpCard[i] = -1;
                            break;
                        }
                    }
                    if (presentSuit == -1)
                    {
                        presentSuit = (int)selected.Suit;
                        history.Add((starter + p) % 4);
                    }
                    history.Add((int)selected.Suit * 13 + (int)selected.Rank);
                    cardInThisTurn[p] = (int)selected.Suit * 13 + (int)selected.Rank;
                }
                int maxPlayer = 0;
                for (int i = 0; i < 3; i++)
                {
                    if (cardInThisTurn[i + 1] / 13 == presentSuit && cardInThisTurn[i + 1] % 13 > cardInThisTurn[maxPlayer] % 13)
                        maxPlayer = i + 1;
                }
                presentSuit = -1;
                starter = (maxPlayer + starter) % 4;
                if (starter == 0 || starter == 2)
                    score += 1;
                printCard(cardInThisTurn);
                Console.WriteLine("round {0} finished!", round);
            }
        }

        private static int[] getRandomCard(int length)
        {
            int[] nums = new int[length];
            Random random = new Random(1);
            for(int i = 0; i < length; i++)
            {
                nums[i] = i;
            }
            for(int i = 0; i < length; i++)
            {
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
                if (card[i] != -1)
                {
                    Console.Write("{0},{1}\t", card[i] / 13, card[i] % 13);
                }
            }
            Console.Write("\n");
        }

        private static GameState GetGameState(int who, int[] hand, int[] dummy, ArrayList history)
        {
            GameState gamestate = new GameState();
            gamestate.TableID = 0;
            gamestate.Vulnerability = Vul.None;
            gamestate.Who = (Player)who;
            if (who == 2)
            {
                int[] t = hand;
                hand = dummy;
                dummy = t;
            }
            gamestate.Hand.AddRange(int2card(hand));
            gamestate.Dummy.AddRange(int2card(dummy));
            if (history.Count == 0)
            {
                gamestate.Dummy.Clear();
            }
            else
            {
                TrickHistory[] playHistory = new TrickHistory[(int)Math.Ceiling((double)history.Count/5)];
                for(int i = 0; i < history.Count; i++)
                {
                    if (i % 5 == 0)
                    {
                        playHistory[i / 5] = new TrickHistory();
                        playHistory[i / 5].Lead = (Player)history[i];
                    }
                    else
                    {
                        Card tmp = new Card();
                        tmp.Rank = (uint)((int)history[i] % 13);
                        tmp.Suit = (Suit)((int)history[i] / 13);
                        playHistory[i / 5].Cards.Add(tmp);
                    }
                }
                gamestate.PlayHistory.AddRange(playHistory);
            }
            gamestate.Contract = new Contract();
            gamestate.Contract.Suit = (Suit)4;
            gamestate.Contract.Level = 3; //默认三无将
            int presentSuit = -1;
            if (history.Count % 5 > 0)
            {
                presentSuit = (int)history[history.Count - history.Count%5 + 1] / 13;
            }
            for(int i = 0; i < hand.Length; i++)
            {
                if (hand[i] != -1 && (hand[i] / 13 == presentSuit || presentSuit == -1))
                {
                    Card tmp = new Card();
                    tmp.Suit = (Suit)(hand[i] / 13);
                    tmp.Rank = (uint)(hand[i] % 13);
                    gamestate.ValidPlays.Add(tmp);
                }
            }
            if (gamestate.ValidPlays.Count == 0)
            {
                for (int i = 0; i < hand.Length; i++)
                {
                    if (hand[i] != -1)
                    {
                        Card tmp = new Card();
                        tmp.Suit = (Suit)(hand[i] / 13);
                        tmp.Rank = (uint)(hand[i] % 13);
                        gamestate.ValidPlays.Add(tmp);
                    }
                }
            }
            return gamestate;
        }

        private static Card[] int2card(int[] hand)
        {
            Card[] hand_card = new Card[hand.Length];
            int count = 0;
            foreach (int i in hand)
            {
                if (i != -1)
                {
                    hand_card[count] = new Card();
                    hand_card[count].Suit = (Suit)(i / 13);
                    hand_card[count].Rank = (uint)(i % 13);
                    count += 1;
                }
            }
            return hand_card.Take(count).ToArray();
        }
    }
}
