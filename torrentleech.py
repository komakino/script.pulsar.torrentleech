# import xbmc
# import cookielib
import urllib, re
# import urllib2

class Torrentleech(object):
    url         = "http://www.torrentleech.org"
    url_login   = url + "/user/account/login/"
    url_query   = url + "/torrents/browse/index/query/%s/%s"

    categories  = {
        'movies' : "1,11,13,14",
        'episodes' : "26,32",
    }

    def __init__(self, provider, username, password):
        self.provider   = provider
        self.username   = username
        self.password   = password
        self.error      = None

        if('Invalid Username/password combination' in self.login().data):
            self.error = 'Invalid Username/password combination!'

    def login(self):
        login_data = urllib.urlencode({
            'username' : self.username,
            'password' : self.password,
        })
        return self.provider.POST(self.url_login, data=login_data)

    def getRegexp(self,r,data):
        match = re.search(r, data)
        if match:
            return match.group(1)
        else: return ''

    def extract_torrents(self,data):
        results = []
        res = {
            'peers': r'Leechers: ([0-9]*)',
            'seeds': r'Seeders: ([0-9]*)',
            'name': r'Torrent Name (.*) Info Hash',
            'info_hash': r'Info Hash ([a-z0-9]*)',
            'size': r'Size ([0-9.]* [A-Z]{2})',
        }

        history = []

        for info in re.findall(r'/torrent/[0-9]*', data):
            if info in history: continue
            history.append(info)

            infoPage = self.provider.GET(self.url + info)

            uri = re.search(r'/download/.*\.torrent', infoPage.data).group(0)

            # torrent = { 'uri': self.provider.with_cookies(self.url + uri) }
            torrent = { 'uri': self.url + uri }
            stripped = re.sub(r'\s{1,}',' ',re.sub('<[^<]+?>', ' ', infoPage.data))
            for r in res:
                torrent[r] = self.getRegexp(res[r], stripped)

            torrent['name'] = " - %s - %s - %s" % (torrent['size'],torrent['name'],self.provider.ADDON.getAddonInfo('name'))

            size = torrent['size'].split(' ')
            if size[1] == 'MB':
                torrent['size'] = int(size[0])*1024*1024
            elif size[1] == 'GB':
                torrent['size'] = int(float(size[0])*1024*1024*1024)

            torrent['peers'] = int(torrent['peers'])
            torrent['seeds'] = int(torrent['seeds'])
            torrent['trackers'] = ['http://tracker.torrentleech.org:2710']

            self.provider.log.info(torrent)
            results.append(torrent)

        self.provider.log.info("Found %s torrents" % len(results))

        return results

    def search(self,query,ttype=None):
        if(ttype and ttype in self.categories):
            category = 'categories/%s' % self.categories[ttype]
        else: 
            category = ''

        response = self.provider.GET(self.url_query % (urllib.quote_plus(query),category))
        return self.extract_torrents(response.data)



# http://www.torrentleech.org/torrents/browse/index/query/would