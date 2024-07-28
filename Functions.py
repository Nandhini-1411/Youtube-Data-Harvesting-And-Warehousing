#import neeeded Libraries 
from googleapiclient.discovery import build
import mysql.connector
from datetime import datetime 
import re

# API key connection
def Api_Key_connection():
    api_service_name = "youtube"
    api_version = "v3"
    youtube = build(api_service_name, api_version, developerKey="AIzaSyB2pYb-X2mofOXT7OPtut6EssEyaII1auE")
    return youtube
youtube = Api_Key_connection()

# Get channel information
def get_channel_info(channel_id):
    data = youtube.channels().list(part="snippet,statistics", id=channel_id).execute()
    for i in data['items']:
        data = dict(
            Channel_Name=i["snippet"]["title"],
            Channel_ID=i["id"],
            Subscribers_Count=i['statistics']['subscriberCount'],
            Views_Count=i["statistics"]["viewCount"],
            Videos_Count=i["statistics"]["videoCount"],
            Channel_Description=i["snippet"]["description"])
    return data
# Get video ids
def get_videos_ids(channel_id):
    video_ids = []
    response = youtube.channels().list(id=channel_id, part='contentDetails').execute()
    Playlist_Id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None
    while True:
        response1 = youtube.playlistItems().list(part='snippet', playlistId=Playlist_Id, maxResults=50, pageToken=next_page_token).execute()
        for i in range(len(response1['items'])):
            video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = response1.get('nextPageToken')
        if next_page_token is None:
            break
    return video_ids
# Get video information
def get_video_info(video_ids,channel_id):
    video_data = []
    response1 = youtube.channels().list(id=channel_id, part='contentDetails').execute()
    Playlist_Id = response1['items'][0]['contentDetails']['relatedPlaylists']['uploads']  
    for video_id in video_ids:
        response = youtube.videos().list(part="snippet,contentDetails,statistics", id=video_id).execute()
        for item in response["items"]:
            published_date = item['snippet']['publishedAt']
            published_date = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
            Duration = item['contentDetails']['duration']
            match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',Duration)
            if match:
                Duration = '{:02}:{:02}:{:02}'.format(*map(int, match.groups(default='0')))
            else:
                Duration = '00:00:00'
            data = dict(
                Video_Id=item['id'],
                Playlist_Id=Playlist_Id,
                Video_Name=item['snippet']['title'],
                Thumbnail=item['snippet']['thumbnails']['default']['url'],
                Video_Description=item['snippet'].get('description'),
                Published_Date=published_date,
                Duration=Duration,
                Views_Count=item['statistics'].get('viewCount'),
                Likes_Count=item['statistics'].get('likeCount'),
                Comments_Count=item['statistics'].get('commentCount'),
                Caption_Status=item['contentDetails']['caption'])
            video_data.append(data)
    return video_data
# Get comment information
def get_comment_info(video_ids):
    next_page_token = None
    Comment_data = []
    for video_id in video_ids:
        while True:
                response = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=50, pageToken=next_page_token).execute()
                for item in response['items']:
                    published_at = item['snippet']['topLevelComment']['snippet']['publishedAt']
                    published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
                    data = {
                            'Comment_Id': item['snippet']['topLevelComment']['id'],
                            'Video_Id': item['snippet']['topLevelComment']['snippet']['videoId'],
                            'Comment_Text': item['snippet']['topLevelComment']['snippet']['textDisplay'],
                            'Comment_Author': item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                            'Comment_Published': published_at
                        }
                    Comment_data.append(data)
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
        return Comment_data
# Get playlist information
def get_playlist_details(channel_id):
    next_page_token = None
    Playlist_data = []
    while True:
        response = youtube.playlists().list(part='snippet', channelId=channel_id, maxResults=50, pageToken=next_page_token).execute()
        response1 = youtube.channels().list(id=channel_id, part='contentDetails').execute()
        Playlist_Id = response1['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        for item in response['items']:
            data = dict(
                Playlist_Id=Playlist_Id,
                Playlist_Name=item['snippet']['title'],
                Channel_Id=item['snippet']['channelId'])
            Playlist_data.append(data)
        next_page_token = response.get('nextPageToken')
        if next_page_token is None:
            break
    return Playlist_data
#connect to db
def create_connection():
    conn = mysql.connector.connect(user='root', password='9876543210', host='127.0.0.1', database='youtube_data')
    return conn
#create tables in db
def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS channel (
            Channel_Id VARCHAR(255) PRIMARY KEY,
            Channel_Name VARCHAR(255),
            Channel_Description TEXT,
            Subscribers_Count INT,
            Videos_Count INT,
            Views_Count INT)""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlist (
            Playlist_Id VARCHAR(255) PRIMARY KEY,
            Channel_Id VARCHAR(255),
            Playlist_Name VARCHAR(255),
            FOREIGN KEY (Channel_Id) REFERENCES channel(Channel_Id))""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS video (
            Video_Id VARCHAR(255) PRIMARY KEY,
            Playlist_Id VARCHAR(255),
            Video_Name VARCHAR(255),
            Video_Description TEXT,
            Published_Date TIMESTAMP,
            Views_Count INT,
            Likes_Count INT,
            Comments_Count INT,
            Duration TIME,
            Thumbnail VARCHAR(255),
            Caption_Status VARCHAR(50),
            FOREIGN KEY (Playlist_Id) REFERENCES playlist(Playlist_Id))""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comment (
            Comment_Id VARCHAR(255) PRIMARY KEY,
            Video_Id VARCHAR(255),
            Comment_Text TEXT,
            Comment_Author VARCHAR(255),
            Comment_Published_Date TIMESTAMP,
            FOREIGN KEY (Video_Id) REFERENCES video(Video_Id))""")
    conn.commit()
#insert data into db
def insert_channel_data(conn, channel_data):
    cursor = conn.cursor()
    sql = """
        INSERT INTO channel (Channel_Id, Channel_Name, Channel_Description, Subscribers_Count, Videos_Count, Views_Count)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            Channel_Id=VALUES(Channel_Id),
            Channel_Name=VALUES(Channel_Name),
            Channel_Description=VALUES(Channel_Description),
            Subscribers_Count=VALUES(Subscribers_Count),
            Videos_Count=VALUES(Videos_Count),
            Views_Count=VALUES(Views_Count)"""
    cursor.execute(sql, (channel_data['Channel_ID'], channel_data['Channel_Name'], channel_data['Channel_Description'], channel_data['Subscribers_Count'], channel_data['Videos_Count'], channel_data['Views_Count']))
    conn.commit()

def insert_playlist_data(conn, playlist_data):
    cursor = conn.cursor()
    sql = """
        INSERT INTO playlist (Playlist_Id, Channel_Id, Playlist_Name)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            Playlist_Name=VALUES(Playlist_Name),
            Playlist_Id=Playlist_Id,
            Channel_Id=VALUES(Channel_Id)"""
    for data in playlist_data:
        cursor.execute(sql, (data['Playlist_Id'], data['Channel_Id'], data['Playlist_Name']))
    conn.commit()
def insert_video_data(conn, video_data):
    cursor = conn.cursor()
    sql = """
        INSERT INTO video (Video_Id, Playlist_Id, Video_Name, Video_Description, Published_Date, Views_Count,
                           Likes_Count, Comments_Count, Duration, Thumbnail, Caption_Status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            Video_Id=VALUES(Video_Id),
            Playlist_Id=VALUES(Playlist_Id),
            Video_Name=VALUES(Video_Name),
            Video_Description=VALUES(Video_Description),
            Published_Date=VALUES(Published_Date),
            Views_Count=VALUES(Views_Count),
            Likes_Count=VALUES(Likes_Count),
            Comments_Count=VALUES(Comments_Count),
            Duration=VALUES(Duration),
            Thumbnail=VALUES(Thumbnail),
            Caption_Status=VALUES(Caption_Status)"""
    for data in video_data:
        cursor.execute(sql,(data['Video_Id'], data['Playlist_Id'], data['Video_Name'], data['Video_Description'], data['Published_Date'], data['Views_Count'], data['Likes_Count'], data['Comments_Count'], data['Duration'], data['Thumbnail'], data['Caption_Status']))
    conn.commit()
def insert_comment_data(conn, comment_data):
    cursor = conn.cursor()
    sql = """
        INSERT INTO comment (Comment_Id, Video_Id, Comment_Text, Comment_Author, Comment_Published_Date)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            Comment_Text=VALUES(Comment_Text),
            Comment_Author=VALUES(Comment_Author),
            Comment_Published_Date=VALUES(Comment_Published_Date)"""
    for data in comment_data:
        cursor.execute(sql, (data['Comment_Id'], data['Video_Id'], data['Comment_Text'], data['Comment_Author'], data['Comment_Published']))
    conn.commit()
#update null values if there is any
def update_null_values(conn):
    cursor = conn.cursor()
    # Update null values in channel table where Channel_Description is null or empty
    cursor.execute('''
            CREATE TEMPORARY TABLE temp_channel_ids
            SELECT Channel_Id
            FROM channel
            WHERE Channel_Description IS NULL OR Channel_Description = ''
        ''')
    cursor.execute('''
                   UPDATE channel c JOIN temp_channel_ids t ON c.Channel_Id = t.Channel_Id SET c.Channel_Description = 'No Description Provided' ''')
    cursor.execute('''DROP TEMPORARY TABLE IF EXISTS temp_channel_ids''')

    # Update null values in video table where Video_Description is null or empty
    cursor.execute('''
            CREATE TEMPORARY TABLE temp_video_ids
            SELECT Video_Id
            FROM video
            WHERE Video_Description IS NULL OR Video_Description = ''
        ''')
    cursor.execute('''UPDATE video v JOIN temp_video_ids t ON v.Video_Id = t.Video_Id SET v.Video_Description = 'No Description Provided' ''')
    cursor.execute('''DROP TEMPORARY TABLE IF EXISTS temp_video_ids''')
    
    # Fill null values in video table for Like_Count and Comment_Count
    cursor.execute('''UPDATE video SET Comments_Count = 0 WHERE Comments_Count IS NULL''')
    cursor.execute('''UPDATE video SET Likes_Count = 0 WHERE Likes_Count IS NULL''')
    conn.commit()

