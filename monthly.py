##################################################################################################################################################################################
#### libraries
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2  import SpotifyClientCredentials
import os
from os import getenv
import argparse
import logging
import json
import time
import sys
from datetime import date, datetime
 

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

##################################################################################################################################################################################
#### dates

    def make_playlist_name(self): #TODO: WHY IS THIS RUNNING TWICE?

        today = date.today()
        year= str(today.year)

        month_no = today.month
        if month_no<10:
            month_no="0"+str(month_no)
        else:
            month_no=str(month_no)

        month_name = today.strftime("%B")

        playlist_name=year + "." + month_no + " " + month_name + " TEST"
        playlist_description="Monthly playlist for "+ month_name + " " +year


        print(playlist_description+ " - Playlist name: " + playlist_name)

        self = MonthlyPlaylist(playlist_name, playlist_description, 0)

        print("****** make_playlist_name ID: ", self.playlist_object_id)

        return  self

##################################################################################################################################################################################
#### functions definition

    def check_for_monthly_playlist_function(self): #check if playlist for the month aready exists

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
            

        print("PLAYLIST ID: ", self.playlist_object_id)
        print("Need to create new playlist? ", str(need_to_create))

        print("****** check_for_monthly_playlist_function ID: ", self.playlist_object_id)

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

        print("****** create_monthly_playlist_function ID: ", self.playlist_object_id)


        return month_playlist_id

    def get_tracks_on_release_radar(self): #return list of tracks to add
        
        #get release radar
        release_radar = sp.playlist_items(playlist_id=release_radar_id)


        #loop through release radar
        for item in release_radar['items']:
            track_id = item['track']['id']
            song_details=str(item['track']['name'])+" - "+ str(item['track']['artists'][0]['name'])
            list_of_tracks_to_add_IDs.append(track_id)
            list_of_tracks_to_add_names.append(song_details)

 ###TODO: do not add if classical or duplicate

            # features = sp.audio_features(track_id)
            # for feature in features:
            #     analysis= sp._get(feature['analysis_url'])
            #     print(json.dumps(analysis, indent=1))
            #     genre=analysis['track']['genre']
            #     genre=str(genre)
            #     if genre != "classical":
            #         print("ok")
            
            #if not classical skip - TODO: fix
            # features = sp.audio_features(track_id)
            # for feature in features:
            #     analysis= sp._get(feature['analysis_url'])
            #     genre=analysis['track']['genre']
            # if genre=="classical":
            #     print("skipping")
            # else:

#add list of song names nad artists, to print when added

        print(list_of_tracks_to_add_IDs, list_of_tracks_to_add_names)
        
        return self, list_of_tracks_to_add_IDs, list_of_tracks_to_add_names

    def upsert_tracks_to_monthly_playlist(self):

        print(self.check_for_monthly_playlist_function(self)[1])

        if self.check_for_monthly_playlist_function(self)[1]:
            self = self.create_monthly_playlist_function(self)
        else:
            self = self.check_for_monthly_playlist_function(self)[0]
        
        print(self)

        playlist_id=str(self.playlist_object_id)

        print (playlist_id)

        #check playlist for track
        #######insert code
        #if track not there, add to playlist
        #######insert code

        print("****** upsert_tracks_to_monthly_playlist ID: ", playlist_id)


        sp.playlist_add_items(playlist_id, list_of_tracks_to_add_IDs, position=None)    
        
        print("Songs added to playlist: ", list_of_tracks_to_add_names)
       

        #tracks_added_to_playlist=0

        return "complete"

    def add_songs_to_library(self):
        print("adding to library: ", list_of_tracks_to_add_names)

        sp.current_user_saved_tracks_add(list_of_tracks_to_add_IDs)
        print("ok")

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

mp.upsert_tracks_to_monthly_playlist(self=MonthlyPlaylist)

mp.add_songs_to_library(self=MonthlyPlaylist)
