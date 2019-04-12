class Song:

    def __init__(self, songname,  artname):
        self.artist = artname
        self.name = songname
        self.upVotes = 0
        self.downVotes = 0

    def __str__(self):
        return self.name + ':' + self.artist

    def getArtist(self):
        return self.artist
    
    def getName(self):
        return self.name
    
    def getUpVotes(self):
        return self.upVotes
    
    def getDownVotes(self):
        return self.downVotes
    
    def UpVote(self):
        self.upVotes += 1
    
    def DownVote(self):
        self.downVotes += 1


    