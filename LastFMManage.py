import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
from pylast import TopItem, Track
import pylast
import pprint
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








'''
###############################################
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
>>>>>>>>>>>>>>>>>>>>>>>> START CODING HERE >>>>
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
###############################################
'''






API_KEY = ''
API_SECRET = ''
username = ''
passwordHash = pylast.md5("")

network = pylast.LastFMNetwork(
	api_key=API_KEY,
	api_secret=API_SECRET,
	username=username,
	password_hash=passwordHash
)


user = network.get_user(username)



def get_time():
	period = {
	0 : "overall",
	1: "7day",
	2: "1month",
	3: "3month",
	4: "6month",
	5: "12month"
}
	print("What time period would you like to work with?")
	time = input("options...\noverall: 0\n7 days: 1\n1 month: 2\n3 months: 3\n6 months: 4\n12 months: 5\n")
	if time.isnumeric():
		time = int(time)
		if 0 <= time <= 5:
			return period[time]
		print("\n")
		return get_time()

def create_pairings(playlist, period):
	lastFM_tracks = user.get_top_tracks(
        period=period, limit=None
    )
	lfm = {}
	for track in lastFM_tracks:
		lfm[str(track.item.title) + ' - ' + str(track.item.artist)] = track.weight
	print("Received Last FM Tracks")
	songs = get_playlist_tracks(playlist, TOKEN)
	print("Received Spotify Tracks")
	pairings = {}
	for x in songs:
		if x["track"] is not None:
			key = x["track"]["name"] + ' - ' + x["track"]["artists"][0]["name"]
			if key in lfm:
				pairings[key] = [lfm[key], x["track"]["id"]]
	return pairings



def get_stats(pairings, ml):
	total = 0
	count = len(pairings.keys())
	maxmin = [0, 1]
	for x in pairings.keys():
		listens = pairings[x][0]
		total += listens
		maxmin[0] = max(listens, maxmin[0])
		maxmin[1] = min(listens, maxmin[1])
	sortedPairs = sorted(pairings.items(), key=lambda item: item[1][0], reverse=ml)
	for i, x in enumerate(sortedPairs):
		print(f"{i+1}/{x[0]}: {x[1][0]} listen{"s" if x[1][0]>1 else ""}")
	print(f"Average listens: {total//count}")
	print(f"Max/Min listens: {maxmin[0]}/{maxmin[1]}")


def remove(pairings, playlist, metric):
	removed_ids = []
	print(f"Removing songs that have been listened {metric} times or less")
	for x in pairings:
		if pairings[x][0] <= metric:
			print(f"Removing {x}")
			removed_ids.append(pairings[x][1])
	sp.playlist_remove_all_occurrences_of_items(playlist, removed_ids)
    



def main():
	print("Welcome. This program will remove least listened to tracks from your playlist.")
	playlist = input("Which playlist would you like to remove from (please use id): ")
	if playlist == "fam" or playlist == "FAM":
		playlist = ""
	period = get_time()
	pairings = create_pairings(playlist, period)
	while(True):
		cmd = input("Given the playlist provided, what would you like to do? stats (s), remove (r): ")
		match cmd:
			case 's':
				mostleast = input("Most or least listened to at the top? (m/l) ")
				mostleast = False if mostleast == 'l' else True
				get_stats(pairings, mostleast)
			case 'r':
				metric = "What is the measure of removing the songs (i.e., if a song is listened to x amount out times, it should be removed): "
				remove(pairings, playlist, int(metric))
			case _:
				continue
	#songs = get_playlist_tracks("","")


main()