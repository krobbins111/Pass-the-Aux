import socket
import datetime
import threading
import time

endThreads = 1

def loopRecv(csoc, size):
    data = bytearray(b" "*size)
    mv = memoryview(data)
    while size:
        rsize = csoc.recv_into(mv,size)
        mv = mv[rsize:]
        size -= rsize
    return data

def addSongMessage(userAlias): #userAlias isn't currently used but might be needed to prevent up/downvoting a song multiple times
    buildMess = "1:1:"
    tryAgain = 1
    while tryAgain == 1:
        songName = str(input("Please enter the name of the song you want to add: "))
        songArtist = str(input("Please enter the artist of the song you want to add: "))
        messSize = str(len(songArtist) + len(songName) + 1)
        while len(messSize) < 3:
            messSize = '0' + messSize #pad the code with zeros to 16 bits if less than that
        tryAgain = 0
        if len(messSize) > 3:
            print("Your song and artist name are too long. They must be less than 998 characters total.\n")
            tryAgain = 1
    return buildMess + messSize + ':' + songName + ':' + songArtist

def upvoteSongMessage(userAlias): #userAlias isn't currently used but might be needed to prevent up/downvoting a song multiple times
    buildMess = "0:1:"
    tryAgain = 1
    while tryAgain == 1:
        songName = str(input("Please enter the name of the song you want to upvote: "))
        songArtist = str(input("Please enter the artist of the song you want to upvote: "))
        messSize = str(len(songArtist) + len(songName) + 1)
        while len(messSize) < 3:
            messSize = '0' + messSize #pad the code with zeros to 16 bits if less than that
        tryAgain = 0
        if len(messSize) > 3:
            print("Your song and artist name are too long. They must be less than 998 characters total.\n")
            tryAgain = 1
    return buildMess + messSize + ':' + songName + ':' + songArtist

def downvoteSongMessage(userAlias): #userAlias isn't currently used but might be needed to prevent up/downvoting a song multiple times
    buildMess = "0:0:"
    tryAgain = 1
    while tryAgain == 1:
        songName = str(input("Please enter the name of the song you want to downvote: "))
        songArtist = str(input("Please enter the artist of the song you want to downvote: "))
        messSize = str(len(songArtist) + len(songName) + 1)
        while len(messSize) < 3:
            messSize = '0' + messSize #pad the code with zeros to 16 bits if less than that
        tryAgain = 0
        if len(messSize) > 3:
            print("Your song and artist name are too long. They must be less than 998 characters total.\n")
            tryAgain = 1
    return buildMess + messSize + ':' + songName + ':' + songArtist


def sendMessage(portNumS, userAlias): #Controls receiving user input, creating the Message, encoding it, and then sending it through the port. Also checks for 'bye' end case
    userStr = str(input(""))
    while len(userStr) > 1 or (userStr != 'A' and userStr != 'a' and userStr != 'U' and userStr != 'u' and userStr == 'D' and userStr == 'd' and userStr == 'E' and userStr == 'e'):
        print("Please enter either: \n'A' to add a song to the queue.\n'U' to upvote a song.\n'D' to downvote a song.\n'E' to exit.\nType anything else for this menu to be printed again.\n")
        userStr = str(input(""))
    if userStr == 'A' or userStr == 'a':
        newMess = addSongMessage(userAlias)
    if userStr == 'U' or userStr == 'u':
        newMess = upvoteSongMessage(userAlias)
    if userStr == 'D' or userStr == 'd':
        newMess = downvoteSongMessage(userAlias)
    if userStr == 'E' or userStr == 'e':
        return 0
    print("Sending message: '" + newMess + "'")

    cSoc = socket.socket()
    # connect to localhost:portnum
    cSoc.connect(("localhost",portNumS))
    cSoc.sendall(newMess.encode("utf-8")) #add replace to specify that if there is a char that cannot be converted to utf-8 it will be replaced with a ?
    commSoc.close()
    return 1


def MCReceive(portNumM):
    
    print("Started multicast receive.")
    mcAddr = "224.0.0.70"
    soc = socket.socket(type=socket.SOCK_DGRAM)
    
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    soc.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
    
    soc.bind(('', (portNumM+1)))
    lHost = socket.gethostbyname("localhost");
    soc.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(lHost))
    
    soc.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(mcAddr) + socket.inet_aton(lHost))
    global endThreads
    while endThreads != 0:
        #print("GOT HERE 1")
        data, addr = soc.recvfrom(1024)
        #print("GOT HERE 2")
        queueRead = str(bytearray(data).decode('utf-8'))
        queueList = queueRead.split(':')
        sizeBytes = queueList.pop(0)
        print("Current Playlist:")
        item = 0
        while item < len(queueList):
            print(queueList[item], "by", queueList[item + 1])
            item += 2
    
    soc.close()
    print("Stopped multicast receive.")

def keepSending(portNumS, userAlias):
    # create the socket
    #  defaults family=AF_INET, type=SOCK_STREAM, proto=0, filno=None
    commSoc = socket.socket()
    
    # connect to localhost:portnum
    commSoc.connect(("localhost",portNumS))
    global endThreads #indicates whether the user has indicated they want to end the program

    #request the song queue
    newMess = "1:0:000:"
    commSoc.sendall(newMess.encode("utf-8")) #add replace to specify that if there is a char that cannot be converted to utf-8 it will be replaced with a ?
    commSoc.close()
    # run the application protocol
    print("Please enter either: \n'A' to add a song to the queue.\n'U' to upvote a song.\n'D' to downvote a song.\n'E' to exit.\nType anything else for this menu to be printed again.\n")
    while( endThreads != 0):
        endThreads = sendMessage(portNumS, userAlias) #CURRENTLY DOESN'T USE userALIAS, but might need to add this later to prevent a user up/downvoting multiple times
    
    # close the comm socket


def joinPlaylist( portNumS, joinCode, userAlias):  #add threading start and handling for if user wants to leave
    # create thread 1, no arguments
    t1 = threading.Thread(name="second", target=MCReceive, args=(portNumS,))
    t2 = threading.Thread(name="first", target=keepSending, args=(portNumS, userAlias))
    
    # create thread 2, 1 argument
    
    # start threads
    t1.start()
    t2.start()
    
    # wait for threads, no timeout
    t1.join()
    t2.join()

    print("Finished. Closing program...")

def recResponse(cSoc, userAlias, joinOrCreate):
    successRead = loopRecv(cSoc,2)
    successRead = str(bytearray(successRead).decode('utf-8'))
    isSuccess = int(successRead[0], 10) #this changes it back into an int and cuts off the : on the end
    if isSuccess == 0: #if the join was not successful, check if you can try again.
        print(isSuccess)
        tryAgainRead = loopRecv(cSoc,1)
        canTryAgain = int(tryAgainRead) #this changes it back into an int and cuts off the : on the end
        if canTryAgain == 1: #can try again
            print ("Your attempt failed. Trying again...\n")
            if joinOrCreate == 1:
                sendCreateMessage(cSoc, userAlias)
            else: #if joinOrCreate == 0
                sendJoinMessage(cSoc)
            return 0
        print ("Your attempt failed. The server will not let you try again.\n")
        return 0
    #if join was successful:
    sizeRead = loopRecv(cSoc,3)
    sizeRead = str(bytearray(sizeRead).decode('utf-8'))
    remainingSize = int(sizeRead[0:2], 10) #this changes it back into an int and cuts off the : on the end
    connectData = loopRecv(cSoc,remainingSize)
    i = 0
    while connectData[i] != 58: #58 is the utf-8 code for a :
        i += 1
    portNumS = int(bytearray(connectData[0:(i)]).decode('utf-8'), 10) #port num to send to
    i += 1
    joinCode = str(bytearray(connectData[i:]).decode('utf-8'))
    print ("The access code for your playlist is " + joinCode)
    cSoc.close()
    joinPlaylist(portNumS, joinCode, userAlias)
    return 1

def sendCreateMessage( cSoc, userAlias):
    while len(userAlias) < 16:
        userAlias = ' ' + userAlias #pad the alias with spaces to 16 bits if less than that
    if len(userAlias) > 16:
        userAlias = userAlias[0:15] #trim to 16 bits if longer than that
    buildMess = "1:" + userAlias
    cSoc.sendall(buildMess.encode("utf-8", "replace"))
    recResponse(cSoc, userAlias, 1)

def sendJoinMessage(cSoc, userAlias):
    joinCode = str(input("Please enter the playlist join code: "))
    while len(joinCode) < 16:
        joinCode = '0' + joinCode #pad the code with zeros to 16 bits if less than that
    if len(joinCode) > 16:
        joinCode = joinCode[-16:-1] #trim to 16 bits if longer that that
    buildMess = "1:" + joinCode
    cSoc.sendall(buildMess.encode("utf-8", "replace"))
    recResponse(cSoc, userAlias, 0)

if __name__ == "__main__":
    commSoc = socket.socket()
    # connect to localhost:50000 (the playlist manager)
    commSoc.connect(("localhost",50000))

    # get an alias from the user (less than 16 char)
    userAlias = str(input("Enter your alias: "))
    while len(userAlias) > 16:
        userAlias = str(input("Please enter an alias less than 16 characters: "))

    joinOrCreate = str(input("Would you like to join a playlist (enter 'J') or create one (enter 'C')?: "))
    while joinOrCreate != 'J' and joinOrCreate != 'j' and joinOrCreate != 'C' and joinOrCreate != 'c':
        joinOrCreate = str(input("Please enter 'J' to join or 'C' to create a playlist: "))

    if joinOrCreate == 'J' or joinOrCreate == 'j':
        sendJoinMessage(commSoc, userAlias)
    if joinOrCreate == 'C' or joinOrCreate == 'c':
        sendCreateMessage(commSoc, userAlias)

