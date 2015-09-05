from pulsar import provider
from torrentleech import Torrentleech

def search(query,ttype):
    client = Torrentleech(provider,'comacino','Kennerth@3802')
    if(client.error):
        provider.log.error(client.error)
        pass

    return client.search(query,ttype=ttype)

def search_episode(episode):
    return search("%(title)s S%(season)02dE%(episode)02d" % episode,'episodes')

def search_movie(movie):
    return search("%(title)s %(year)d" % movie,'movies')

provider.register(search, search_movie, search_episode)