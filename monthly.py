##################################################################################################################################################################################
#### libraries
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from os import getenv
from datetime import date
 

##################################################################################################################################################################################
#### Spotify params
spotify_client_id = os.getenv('SPOTIPY_CLIENT_ID', 'client_id')
spotify_secret = os.getenv('SPOTIPY_CLIENT_SECRET', 'secret')
spotify_redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI', 'redirect_uri')
spotify_api_url = os.getenv('api_url', 'api_url')
release_radar_id = os.getenv('release_radar_id', 'release_radar_id')

##################################################################################################################################################################################
#### setup
scope = "playlist-modify-public playlist-read-private playlist-read-collaborative playlist-modify-private user-library-read playlist-read-private user-library-modify user-read-private" 
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
sp.trace = True
user_id = sp.me()['id']
list_of_tracks_to_add_IDs=[]
list_of_tracks_to_add_names=[]


class MonthlyPlaylist(object):
    def __init__(self, playlist_object_title, playlist_object_description, playlist_object_id):
        self.playlist_object_title = playlist_object_title
        self.playlist_object_description = playlist_object_description
        self.playlist_object_id = playlist_object_id
    pass

    def make_playlist_name(self): #generate playlist name #>>>>>>>>>>>>>>>>>>>>>>>>>>TODO: WHY IS THIS RUNNING MULTIPLE TIMES?!

        today = date.today()
        year= str(today.year)

        month_no = today.month
        if month_no<10:
            month_no="0"+str(month_no)
        else:
            month_no=str(month_no)

        month_name = today.strftime("%B")

        playlist_name=year + "." + month_no + " " + month_name + " TESTING"
        playlist_description="Monthly playlist for "+ month_name + " " +year

        self = MonthlyPlaylist(playlist_name, playlist_description, 0)

        return  self

    def check_for_monthly_playlist_function(self): #check if playlist for the month aready exists #>>>>>>>>>>>>>>>>>>>>>>>>>>TODO: WHY IS THIS RUNNING MULTIPLE TIMES?!

        self = self.make_playlist_name(self)

        playlist_name_for_lookup = str(self.playlist_object_title)

        need_to_create = True
    
        all_playlists = sp.current_user_playlists(limit=50, offset=0)

        for i, playlist in enumerate(all_playlists['items']):
            if playlist_name_for_lookup in str(playlist):
                self.playlist_object_id = playlist['id']
                need_to_create = False
                print("A playlist called "+ playlist_name_for_lookup+" already exists. ID: "+ self.playlist_object_id)

        if need_to_create:
            print("Please create a new playlist called "+playlist_name_for_lookup)
            self.playlist_object_id = 0
            
        print("Need to create new playlist? ", str(need_to_create))

        return self, need_to_create
    
    def create_monthly_playlist_function(self): #create monthly playlist

        self = self.make_playlist_name(self)
        
        playlist_name = str(self.playlist_object_title)
        playlist_description=str(self.playlist_object_description)

        new_playlist= sp.user_playlist_create(user_id, playlist_name, public=True, collaborative=False, description=playlist_description)
        month_playlist_id=new_playlist['id']
        self.playlist_object_id = month_playlist_id

        playlist_url=new_playlist['external_urls']['spotify']
        print("New playlist: "+ month_playlist_id+ " - "+ playlist_url)

        return month_playlist_id

    def get_tracks_on_release_radar(self): #return list of tracks to add
        
        if self.check_for_monthly_playlist_function(self)[1]:
            self = self.create_monthly_playlist_function(self)
        else:
            self = self.check_for_monthly_playlist_function(self)[0]
        
        playlist_id=str(self.playlist_object_id)

        #check playlist for track
        this_playlist = sp.playlist_items(playlist_id=playlist_id)
        playlist_tracks_so_far = []
    
        for item in this_playlist['items']:
            track_id = item['track']['id']
            playlist_tracks_so_far.append(track_id)

        playlist_list_string = str(playlist_tracks_so_far)

        #get release radar
        release_radar = sp.playlist_items(playlist_id=release_radar_id)

        #get monthly playlist
        playlist_id=self.playlist_object_id
        
        #loop through release radar
        for item in release_radar['items']:
            track_id = item['track']['id']
            song_details=str(item['track']['name'])+" - "+ str(item['track']['artists'][0]['name'])
            artist = sp.artist(item['track']["artists"][0]["external_urls"]["spotify"])
            genres = artist["genres"]
            if "classical" not in str(genres):
                if str(track_id) not in playlist_list_string:
                    list_of_tracks_to_add_names.append(song_details)
                    list_of_tracks_to_add_IDs.append(track_id)          
        
        return self, list_of_tracks_to_add_IDs, list_of_tracks_to_add_names

    def add_tracks_to_monthly_playlist(self): #WHY IS THIS RUNNING TWICE

        self = self.get_tracks_on_release_radar(self)[0]

        playlist_id=str(self.playlist_object_id)

        if list_of_tracks_to_add_IDs:
            sp.playlist_add_items(playlist_id, list_of_tracks_to_add_IDs, position=None)
            sp.current_user_saved_tracks_add(list_of_tracks_to_add_IDs)
            print("Songs added to library: ", list_of_tracks_to_add_names)
        else:
            print("Nothing to add")

        return "ok"

#################################################################################################################################################################################
### functions calling

mp = MonthlyPlaylist

mp.make_playlist_name(self=MonthlyPlaylist)

mp.check_for_monthly_playlist_function(self=MonthlyPlaylist)

if mp.check_for_monthly_playlist_function(self=MonthlyPlaylist)[1]:
    mp.create_monthly_playlist_function(self=MonthlyPlaylist)
    print("New playlist created.")
else:
    print("No new playlist required.")

mp.get_tracks_on_release_radar(self=MonthlyPlaylist)

mp.add_tracks_to_monthly_playlist(self=MonthlyPlaylist)