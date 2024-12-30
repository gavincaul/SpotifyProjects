import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
import logging
import pprint
import random

logging.getLogger('spotipy').setLevel(logging.CRITICAL)


CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URI = 'https://localhost:8888'
USERNAME = ''
SCOPE = 'playlist-modify-public'


def getToken():
    try:
        sp_oauth = SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope=SCOPE, username=USERNAME)
        token_info = sp_oauth.get_cached_token()

        if token_info and sp_oauth.is_token_expired(token_info):
            refresh_token = token_info["refresh_token"]
            new_token_info = sp_oauth.refresh_access_token(refresh_token)
            return new_token_info["access_token"]

        return sp_oauth.get_access_token(code=None, as_dict=False)
    except spotipy.oauth2.SpotifyOauthError as e:
        print(f"Error with spotipy OAuth: {e}")
        return None

TOKEN = getToken()
sp = spotipy.Spotify(auth=TOKEN)

def link(uri, label=None):
    if label is None: 
        label = uri
    parameters = ''

    # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST 
    escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'

    return escape_mask.format(parameters, uri, label)

"""
def topsongs(playlist):
    above98 = []
    offset = 0
    data = sp.playlist_items(playlist, offset=offset)   
    while(offset < 8600):
        data = sp.playlist_items(playlist, offset=offset)   
        for x in data['items']:
            try: 
                if(x["track"]["popularity"] == 17):
                    #print(x["track"]["popularity"])
                    above98.append(x["track"]["name"] + "-" + x["track"]["artist"])
            except:
                continue
        offset+=100
    pprint.pprint(above98)
"""
                



def generateMix(source, dest, genre):
    data = sp.playlist_items(source, limit=1)
    offset = 0
    total_songs = data["total"]
    while(offset < total_songs):
        try:
            data = sp.playlist_items(source, offset=offset)
            offset+=100
            for x in data['items']:
                if(genre in sp.artist(x["track"]["artists"][0]["id"])["genres"]):
                    sp.user_playlist_add_tracks(USERNAME, dest, [x["track"]["id"]])
                    tid = x["track"]["name"]
                    print(f"Added {tid}")
        except Exception as e:
            print(e)





def checkPlaylist(playlist):
    try:
        sp.playlist(playlist, additional_types=('track',))
        return True
    except spotipy.exceptions.SpotifyException as e:
        #print(f"Error: {e}")
        return False

def checkGenre(genre):
    with open("./spotify-genres.md", 'r') as f:
        for line in f:
            if genre in line.lower():
                return True
    return False

def createPlaylist(genre):
    createdPlaylist = sp.user_playlist_create(USERNAME, f"{genre} Mix (MM)", public=True, collaborative=False, description='')
    return createdPlaylist["id"]

def reorderPlaylist(source):
    song_iter = 0
    data = sp.playlist_items(source, limit=1)
    offset = 0
    total_songs = data["total"]
    while(offset < total_songs):
        try:
            data = sp.playlist_items(source, offset=offset)
            offset+=100
            for x in data['items']:
                sp.playlist_reorder_items(x["track"]["id"], song_iter, insert_before=random.randint(1, total_songs-1))
                song_iter += 1
        except Exception as e:
            print(e)

def checkStats():
    i = input("Artist: 1, Song: 2, Album: 3: ")
    v = input("-> ")
    match(int(i)):
        case 1:
            results = sp.search(q='artist:' + v, type='artist')
            items = results['artists']['items']
            pprint.pprint(items)
            #pprint.pprint(sp.artist(v))
        case 2:
            pprint.pprint(sp.track(v))
        case 3:
            pprint.pprint(sp.album(v))


def __main__():
    exit = False

    while(not exit):
        createplaylist=False
        print("Welcome to MixMaker--Generate a mix playlist based on a genre\n")
        source_playlist = input("What playlist would you like to generate FROM? (please use playlist_id): ")
        if(source_playlist == "stats"): 
            checkStats()
            continue
        if(not checkPlaylist(source_playlist)):
            print("That playlist does not exist. Please try again\n")
            continue
        dest_playlist = input("What playlist would you like to use for the mix? (leave blank if you want a playlist generated): ")
        if(not checkPlaylist(dest_playlist)):
            print("That playlist does not exist. Creating a new one based on the genre\n")
            createplaylist=True
        genre = input("Finally, what genre would you like to create? " + link("https://gist.github.com/andytlr/4104c667a62d8145aa3a", "list of genres") + ": ")
        if(not checkGenre(genre.lower())):
            print("That genre does not exist. Please double check.\n")
        if(createplaylist):
            dest_playlist = createPlaylist(genre)
        print("Generating...")
        generateMix(source_playlist, dest_playlist, genre.lower())
        shuffle = input("Shuffle/Reorder playlist? (0 or 1): ")
        if(int(shuffle)):
            reorderPlaylist(dest_playlist) 
        

    return 0


__main__()