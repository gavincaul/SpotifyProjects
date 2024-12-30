import pprint
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
CLIENT_SECRET = ''
CLIENT_ID = ''
REDIRECT_URI = 'https://localhost:8888'
USERNAME = '' 
SCOPE = 'playlist-modify-public'

"""

FUNCTION: getToken

Retrieves refreshed token from Spotify API

@params: None

@returns: api token

"""

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
sp = spotipy.Spotify(auth=getToken())


"""
FUNCTION: get_playlist_tracks

Accesses a playlist (that exists) and returns the JSON of each song into an array

@params:
	playlist_id: str of the playlist id
	token: API token provided by Spotify API

@returns:
	songs: list of songs ([] empty list in case of error)

"""

def get_playlist_tracks(playlist_id, token):

	if token is None:
		print("Error: Access token is not available.")
		return []
	try:
		sp.playlist(playlist_id, additional_types=('track',))
	except spotipy.exceptions.SpotifyException as e:
		print(f"ERROR: Playlist doesn't exist")
		print("err_code: {e}")
		return []
	data = sp.playlist_items(playlist_id, limit=1)
	total_songs = data["total"]
	offset = 0
	songs = []

	while(offset < total_songs):
		try:
			sp.trace = False
			data = sp.playlist_items(playlist_id, offset=offset)
			offset+=100
			for x in data['items']:
				songs.append(x)
		except Exception as e:
			print(f"ERROR: {e}")
	return songs


def checkStats(token):
	sp = spotipy.Spotify(auth=token)
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








'''
###############################################
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
>>>>>>>>>>>>>>>>>>>>>>>> START CODING HERE >>>>
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
###############################################
'''

def converttostnd(ms):
    ms = ms // 1000
    return [(ms // 60), (ms - 60 * (ms // 60))]

def filterSongs(playlist, numMins):
	idList = []
	for x in playlist:
		if x["track"]:
			if converttostnd(int(x["track"]["duration_ms"]))[0] >= numMins:
				idList.append(x["track"]["id"])
	return idList


def getIDs(playlist):
    ids = []
    for song in playlist:
        if song["track"]["id"]:
            ids.append(song["track"]["id"])
    return ids
		

		



def main():

	FAMSongs = get_playlist_tracks("",TOKEN)
	looongSongs = get_playlist_tracks("", TOKEN)
	filtered = filterSongs(FAMSongs, 7)
	longIDs = getIDs(looongSongs)
	adding = [item for item in filtered if item not in longIDs and item is not None]
	sp.playlist_add_items("", adding)

	#checkStats("")
main()