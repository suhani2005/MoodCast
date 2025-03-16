import csv
from googleapiclient.discovery import build   #Imports the build function from the googleapiclient.discovery module. 
#This function is used to build a client object for interacting with the YouTube Data API.
from collections import Counter   #Imports the Counter class from the collections module, which is useful for counting occurrences of items, although it is not used in this script.
import streamlit as st
from senti import extract_video_id   #used to extract the video ID from a YouTube link.
from googleapiclient.errors import HttpError   #used to handle errors related to the YouTube Data API.
import warnings   #which allows the management of warning messages in the script.
warnings.filterwarnings('ignore')  #gnores any warning messages that would be printed during execution, 


#YouTube API Setup
DEVELOPER_KEY= "API KEY" # Retrieves the YouTube API key stored in Streamlit's secrets management system
YOUTUBE_API_SERVICE_NAME='youtube'      #efines the name of the API service, which is youtube.
YOUTUBE_API_VERSION='v3'
#Uses the build function from the Google API client to create a client object (youtube) for interacting with the YouTube Data API.
youtube= build(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)


def get_channel_id(video_id):
    #This sends a request to the YouTube Data API's videos().list method to get information about the video specified by video_id. The part='snippet' indicates that we only need the snippet part of the video resource, which includes the channel ID.
    response=youtube.videos().list(part='snippet',id=video_id).execute()
    #Extracts the channelId from the API response. The response is a list of items, and the channelId is located within the snippet of the first item.
    channel_id=response['items'][0]['snippet']['channelId']
    return channel_id

def save_comments(video_id):
    comment = []
    # Request comments from YouTube API
    results = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText'
    ).execute()
      
    # A while loop is used to handle pagination of comments
    while results:
        for item in results['items']:
            # Extracts actual text of toplevelcomment
            comment_text = item['snippet']['topLevelComment']['snippet']['textDisplay']
            # Extracts username of the comment author
            username = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            comment.append([username, comment_text])
    
        # Checks if API response includes a nextpagetoken, which indicates there are more comments to retrieve
        if 'nextPageToken' in results:
            nextPage = results['nextPageToken']  # retrieves the token to request next page
            results = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                textFormat='plainText',
                pageToken=nextPage
            ).execute()
        else:
            break  # if there is no token, exit the loop

    filename = video_id + '.csv'  # creates a filename for csv file by appending .csv to video_id
    
    # Opens a new csv file for writing and writes all comments within the 'with' block
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Username', 'comment'])
        for item in comment:
            writer.writerow([item[0], item[1]])
    
    return filename  # Return the filename after the file is properly closed

  # This should be outside the with block but properly indented
#function to retrieve the statistics of a YouTube video, such as views, likes, and comments.      
def get_video_stats(video_id):
    try:
        #ends a request to the YouTube API to get statistics for the specified video, specifying part='statistics' to retrieve the statistics.
        response = youtube.videos().list(
            part='statistics',
            id=video_id
        ).execute()

        return response['items'][0]['statistics']
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None


#Function to retrieve information about a YouTube channel, such as its title, subscriber count, video count, and description.
def get_channel_info(youtube, channel_id):
    try:
        response = youtube.channels().list(
            part='snippet,statistics,brandingSettings',
            id=channel_id
        ).execute()

        channel_title = response['items'][0]['snippet']['title']
        video_count = response['items'][0]['statistics']['videoCount']
        channel_logo_url = response['items'][0]['snippet']['thumbnails']['high']['url']
        channel_created_date = response['items'][0]['snippet']['publishedAt']
        subscriber_count = response['items'][0]['statistics']['subscriberCount']
        channel_description = response['items'][0]['snippet']['description']
        
        channel_info = {
        'channel_title': channel_title,
    'video_count': video_count,
    'channel_logo_url': channel_logo_url,
    'channel_created_date': channel_created_date,
    'subscriber_count': subscriber_count,    # Note this key name
    'channel_description': channel_description
}
        

        return channel_info

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None
