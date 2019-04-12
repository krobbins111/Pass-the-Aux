import selectors
import socket
from PlaylistServer import PlaylistServer

def loopRecv(csoc, size):
    data = bytearray(b" "*size)
    mv = memoryview(data)
    while size:
        rsize = csoc.recv_into(mv,size)
        mv = mv[rsize:]
        size -= rsize
    return data

class PlaylistManager:
    
    def __init__(self):
        self.instances = [PlaylistServer(50001, "sixteencharsgood"), PlaylistServer(50002, "chars4dayzzzzzzz")]

    def addInstance(self, name):
        #make instance
        self.instances.append(instance) 

    def joinInstance(self, code, csoc):
        for instance in self.instances:
            if code == instance.code:
                # commSoc = socket.socket()
                # commSoc.connect(("localhost", instance.getIP()))
                print("found")
                csoc.sendall(('1:' + str(len(str(instance.getIP()))+17) + ':' + str(instance.getIP()) + ':' + instance.getCode()).encode("utf-8"))
                return 1
        print("Could not find playlist. Received: " + code)
        csoc.sendall('0'.encode("utf-8"))

    def handleMessage(self, csoc):
        join = False
        create = False
        size_read = loopRecv(csoc,2)
        joinOrCreate = int(size_read[0]) #this changes it back into an int and cuts off the : on the end
        print(joinOrCreate)
        if joinOrCreate == 48:
            create = True
        elif joinOrCreate == 49:
            join = True
        data_read = loopRecv(csoc,16)
        data = str(bytearray(data_read).decode('utf-8'))
        if join:
            self.joinInstance(data, csoc)
        elif create:
            self.addInstance(data, csoc)
        



if __name__ == "__main__":

    pm = PlaylistManager()
    
    # create the selector
    sel = selectors.DefaultSelector()
    
    
    # create the server socket
    #  defaults family=AF_INET, type=SOCK_STREAM, proto=0, filno=None
    serversoc = socket.socket()
    
    # make is non blocking
    # serversoc.setblocking(False)
    
    # bind to local host:5000
    serversoc.bind(("localhost",50000))
                   
    # make passive with backlog=5
    serversoc.listen(5)
    
    # register the server socket
    # sel.register(serversoc, selectors.EVENT_READ, doAccept)
    # wait for incoming connections
    while True:
        keepgoing = 1
        print("Listening on ", 50000)
        commsoc, raddr = serversoc.accept()
        while keepgoing:
            pm.handleMessage(commsoc)
            keepgoing = 0
        commsoc.close()

    
    # close the server socket
    serversoc.close()
