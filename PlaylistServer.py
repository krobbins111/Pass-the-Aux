import socket
import selectors
import datetime
from Song import Song
import random
import string
import threading

def loopRecv(csoc, size):
    data = bytearray(b" "*size)
    mv = memoryview(data)
    while size:
        rsize = csoc.recv_into(mv,size)
        #print("read", rsize)
        mv = mv[rsize:]
        size -= rsize
    return data

rand_str = lambda n: ''.join([random.choice(string.ascii_lowercase) for i in range(n)])

class PlaylistServer:

    def __init__(self, ip, code):
        self.listeners = []
        self.songQueue = [Song("hello", "world")]
        #self.code = rand_str(16)
        self.code = code
        self.ip = ip

    def getCode(self):
        return self.code

    def getIP(self):
        return self.ip
    
    def UpVoteSong(self, songName, artist):
        for song in self.songQueue:
            if song.artist == artist and song.name == songName:
                song.UpVote()

    def DownVoteSong(self, songName, artist):
        for song in self.songQueue:
            if song.artist == artist and song.name == songName:
                song.DownVote()
                if song.getDownVotes() > 2:
                    self.songQueue.remove(song)

    def MakeQueueString(self):
        queueStr = ''
        for song in self.songQueue:
            queueStr += ':' + str(song)
        strlen = len(queueStr)
        if strlen < 100:
            strlen = '0' + str(strlen)
        else:
            strlen = str(strlen)
        return strlen + queueStr


    def handleMessage(self, csoc, userSetPortNum):
        add = 49
        up = 49
        vote = 48
        down = 48
        addOrVoteRead = loopRecv(csoc,2)
        #addOrVoteRead = str(bytearray(addOrVoteRead).decode('utf-8'))
        addOrVote = int(addOrVoteRead[0])
        print("AorV: ", addOrVote)
        upOrDownVoteRead =  loopRecv(csoc,2)
        #upOrDownVoteRead = str(bytearray(upOrDownVoteRead).decode('utf-8'))
        upOrDownVote = int(upOrDownVoteRead[0])
        print("UorV: ", upOrDownVote)
        sizeRead = loopRecv(csoc, 4)
        #sizeRead = str((sizeRead).decode('utf-8'))
        index = 0
        size = ''
        while index < 3:
            size += str(int(sizeRead[index]) - 48)
            index += 1
        size = int(size)
        songAndArtistRead = loopRecv(csoc, size)
        songAndArtist = str(bytearray(songAndArtistRead).decode('utf-8'))
        if size == 0:
            song = ''
            artist = ''
        else:
            songAndArtist = songAndArtist.split(':')
            song = songAndArtist[0]
            artist = songAndArtist[1]
            print(song)
            toQueue = Song(song, artist)
        if addOrVote == add and upOrDownVote == up:
                #add song object to queue
                print("adding", song,"by", artist)
                self.songQueue.append(toQueue)
        elif addOrVote == vote:
            #change vote attribute
            if upOrDownVote == up:
                #up on song
                print("upvoting", song,"by", artist)
                self.UpVoteSong(song, artist)
            elif upOrDownVote == down:
                #down on song
                print("downvoting", song,"by", artist)
                self.DownVoteSong(song,artist)
        #send full queue in message back to listener
        #set up multicast socket
        esoc = socket.socket(type=socket.SOCK_DGRAM)
        mcAddr = "224.0.0.70"
        mcPort = userSetPortNum+1
        esoc.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        #esoc.bind((mcAddr,mcPort))
        lhost = socket.gethostbyname("localhost")
        esoc.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(lhost))
        
        esoc.sendto(self.MakeQueueString().encode("utf-8"), ( mcAddr, mcPort))
        print("Hello World")
        esoc.close()
    
    def create(self):
        userSetPortNum = int(input("Enter the port to listen at and multicast too: "))
        # create the selector
        sel = selectors.DefaultSelector()
        # create the server socket
        #  defaults family=AF_INET, type=SOCK_STREAM, proto=0, filno=None
        serverSoc = socket.socket()
        #serverSoc.setblocking(False)
        
        # bind to local host:userSetPortNum
        serverSoc.bind(("localhost",userSetPortNum))
        # make passive with backlog=5
        serverSoc.listen(5)
        
        self.ip = userSetPortNum
        
        # wait for incoming connections
        
        while True:
            print("Listening on", userSetPortNum)
            print(self.getCode())
            #sel.select()
            commsoc, raddr = serverSoc.accept()
            print("Connection from:", raddr)
            # register
            #sel.register(commsoc, selectors.EVENT_READ, self.handleMessage(commsoc, userSetPortNum))
            self.handleMessage(commsoc, userSetPortNum)
            commsoc.close()

        # close the server socket
        serverSoc.close()

if __name__ == "__main__":
    
    ps = PlaylistServer(50001, "sixteencharsgood")
    ps2 = PlaylistServer(50002, "chars4dayzzzzzzz") #7 z's
    # create thread 1, no arguments
    t1 = threading.Thread(name="second", target= ps.create)
    t2 = threading.Thread(name="first", target=ps2.create)
    
    # create thread 2, 1 argument
    
    # start threads
    t1.start()
    t2.start()
    
    # wait for threads, no timeout
    t1.join()
    t2.join()

    print("Finished. Closing program...")
    
