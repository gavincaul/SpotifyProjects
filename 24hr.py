import random
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
import datetime
import pprint
CLIENT_SECRET = ''
CLIENT_ID = ''
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


def converttostnd(ms):
    ms = ms // 1000
    return [(ms // 60), (ms - 60 * (ms // 60))]# [minutes,seconds]
    

TOKEN = getToken()


def get_playlist(total_songs, token):
    offset = 0
    if token is None:
        print("Error: Access token is not available.")
        return 
    sp = spotipy.Spotify(auth=token)
    gavin = 0
    aidan = 0
    gavinSecondTotal = 0
    aidanSecondTotal = 0
    track_names = {}
    while(offset < total_songs):
        try:
            playlist_id = ''

            sp.trace = False
            data = sp.playlist_items(playlist_id, offset=offset)
            offset+=100
            for x in data['items']:
                # Check if the request was successful
                added_by = x['added_by']
                user_name = added_by['id'].split("/")[-1]
                track_info = x['track']
                track_name = track_info['name']
                ms = x["track"]["duration_ms"]
                time = converttostnd(ms)  # minutes = time[0], seconds = time[1]
                # Print the parsed information
                if (user_name == ""):
                    user_name = "Gavin"
                    gavin += 1
                    gavinSecondTotal += ms
                else:
                    user_name = "Aidan"
                    aidan += 1
                    aidanSecondTotal += ms
                print(f"\n-------------\nUser ID: {user_name}")
                print(f"Track Name: {track_name}")
                print(f"Track Length: {time[0]} minutes {time[1]} seconds\n-------------\n")
                if track_name in track_names:
                    track_names[track_name].append(track_name)
                else:
                    track_names[track_name] = [track_name]

        except spotipy.oauth2.SpotifyOauthError as e:
            print(f"Error refreshing access token: {e}")
        except spotipy.SpotifyException as e:
            print(f"Error adding song to playlist: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    gavlist = converttostnd(gavinSecondTotal)
    aidlist = converttostnd(aidanSecondTotal)
    print(f"Gavin: {gavin} songs; Total time: {gavlist[0]//60} hours {gavlist[0]-(60*(gavlist[0]//60))} minutes {gavlist[1]} seconds")
    print(f"Aidan: {aidan} songs; Total time: {aidlist[0]//60} hours {aidlist[0]-(60*(aidlist[0]//60))} minutes {aidlist[1]} seconds")
    print(f"Gavin Average: {str(datetime.timedelta(seconds=gavinSecondTotal//1000//gavin))[3:]}")
    print(f"Aidan Average: {str(datetime.timedelta(seconds=aidanSecondTotal//1000//aidan))[3:]}")
    print(f"Total Songs: {gavin+aidan}, Total time: {(gavlist[0] + aidlist[0])//60} hours {(gavlist[1] + aidlist[1]) - 60* ((gavlist[1] + aidlist[1])//60)} minutes")

    print("\nDuplicate Songs:")
    for track_name, track_ids in track_names.items():
        if len(track_ids) > 1:
            print(f"Track Name: {track_name}")
    print()


def compile_names(total_songs):
    offset = 0
    all_songs = {}
    song_iter = 0
    while(offset < total_songs):
        try:
            playlist_id = ''
            sp.trace = False
            data = sp.playlist_items(playlist_id, offset=offset)
            offset+=100
            for x in data['items']:
                all_songs[(x["track"]["name"])] = song_iter
                song_iter += 1
        except spotipy.oauth2.SpotifyOauthError as e:
            print(f"Error refreshing access token: {e}")
        except spotipy.SpotifyException as e:
            print(f"Error adding song to playlist: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    return all_songs








def balance_songs(delimiter, total_songs):
    offset = 0
    song_iter = 0
    prev = False
    moved = False
    playlist_id = ''
    while(offset < total_songs):
        try:
            sp.trace = False
            data = sp.playlist_items(playlist_id, offset=offset)
            offset+=100
            for x in data['items']:
                if(prev):
                    if(converttostnd(x["track"]["duration_ms"])[0] >= delimiter):
                        sp.playlist_reorder_items(playlist_id, song_iter, insert_before=random.randint(1, total_songs-1))
                        print("Moved " + x["track"]["name"])
                        moved = True
                    else:
                        prev = False
                elif(converttostnd(x["track"]["duration_ms"])[0] >= delimiter):
                    prev = True
                song_iter += 1
        except spotipy.oauth2.SpotifyOauthError as e:
            print(f"Error refreshing access token: {e}")
        except spotipy.SpotifyException as e:
            print(f"Error adding song to playlist: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


    if(moved):
        moved = False
        balance_songs(delimiter, total_songs)



while(True): 
    sp = spotipy.Spotify(auth=TOKEN)
    playlist_id = ''
    choice = input("\'reorder,\' \'balance (12 mins),\' \'stats,\' or \'exit\': ")
    choice = choice.split(" ")
    data = sp.playlist_items(playlist_id, limit=1)
    total_songs = data["total"]
    song_delimiter = 12
    if(choice[0] == "stats"):
        if(len(choice)>1):
            total_songs = int(choice[1])
        get_playlist(total_songs, TOKEN)
    elif(choice[0] == "reorder"):
        compiled_names = compile_names(total_songs)
        song_1 = input("Song 1: ")
        found = False
        for song in compiled_names.keys():
            if(song_1.lower() == song.lower()):
                print(f"Song 1 == {song}")
                song_1 = song
                found = True
        if(found):
            song_2 = input("Song 2: ")
            found = False
            for song in compiled_names.keys():
                if(song_2.lower() == song.lower()):
                    print(f"Song 2 == {song}")
                    found = True
                    song_2 = song
            if(found):
#               print(f"\"{song_1}\" position: {compiled_names[song_1]}")   
#               print(f"\"{song_2}\" position: {compiled_names[song_2]}")   
                sp.playlist_reorder_items(playlist_id, compiled_names[song_2], insert_before=compiled_names[song_1]+1)
                print("Reordering...")
                compiled_names = compile_names(total_songs)
#               print(f"\"{song_1}\" position: {compiled_names[song_1]}")   
#               print(f"\"{song_2}\" position: {compiled_names[song_2]}")   
                print("Complete")
            else:
                print("Song not found")
        else:
            print("Song not found")
    elif(choice[0] == "balance"):
        if(len(choice)>1):
            song_delimiter = choice[1]
        balance_songs(int(song_delimiter), total_songs)
    elif(choice[0] == "exit"):
        print("Bye.")
        exit(0)
    elif(choice[0] == "print"):
        pprint.pprint(data)
    else:
        print("Invalid choice")



