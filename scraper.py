import re
import time
import sys
import requests
from bs4 import BeautifulSoup
import SECRETS


def getLyricsFromURL(url, regex, keepchars = ".+-'()&$"):
    """Given URL/to/song, scrape Rap Genius and save lyrics as ./<Song_Title>"""
    soup = BeautifulSoup(requests.get(url).content, 'lxml')

    title_raw = soup.h1.get_text()
    #title = ''.join(c if c.isalnum() or c in keepchars
                    #else '_' for c in title_raw.rstrip()).lower()
    title = re.sub(' ', '_', title_raw.rstrip().lower())

    # get lyrics with song section breaks
    lyrics_raw = ''.join(lyr.get_text() for lyr in soup.lyrics.find_all(['b','p']))
    lyrics = re.sub(regex, '', lyrics_raw).strip() + '\n' # rm leading \n only

    with open(title, 'w') as f:
        try:
            f.write(lyrics.encode("UTF-8"))
        except:
            import code; code.interact(local=locals())

    print '{}, scraped...'.format(title)


def getSongURLsByArtist(artist):
    """Given name of artist, return generator of song lyric URLs"""
    params = {'access_token': SECRETS.CLIENT_ACCESS,
              'per_page': 50,
              'sort': 'popularity'}
    artist_id = getArtistID(artist)
    base_url = 'https://api.genius.com/artists/{}/songs'.format(artist_id)
    hits = requests.get(base_url, params).json()
    #outfile = "TODO" ??
    return (song['url'] for song in hits['response']['songs'])


def getArtistID(artist):
    """Given keyword/s to search using Genius API, return artist ID (int)"""
    params = {'access_token': SECRETS.CLIENT_ACCESS,
              'q': artist}
    base_url = 'https://api.genius.com/search'
    hits = requests.get(base_url, params).json()
    try:
        # artist ID of first matching song
        return hits['response']['hits'][0]['result']['primary_artist']['id']
    except(IndexError):
        print 'No hits ):'
        raise


#def doWork(file_in):
    ## regex to remove `[HEADERS]`
    #to_remove = re.compile('\[[^\]]*\]')
    #with open(file_in, 'r') as f:
        #for url in f.xreadlines():
            #getLyricsFromURL(url.rstrip(), to_remove)
            #time.sleep(5)


def doWork(artist):
    # regex to remove `[HEADERS]`
    to_remove = re.compile('\[[^\]]*\]')
    for url in getSongURLsByArtist(artist):
        getLyricsFromURL(url, to_remove)
        time.sleep(5)


if __name__ == "__main__":
    try:
        KEYWORD = sys.argv[1]
    except(IndexError):
        KEYWORD = "kendrick lamar"
    doWork(KEYWORD)
