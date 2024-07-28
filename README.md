# Youtube-Data-Harvesting-And-Warehousing
-Collect and Analyze YouTube data, including data processing and storage.

-Built a Streamlit app to fetch and display data from a MySQL database

---------------------------------------------------------------------
**1. Import Libraries and Set Up API Connection:**
   - Import necessary libraries for connecting to YouTube API, MySQL, pandas, Streamlit, and datetime.
   - The Libraries are,
        - googleapiclient.discovery – For API Connection and Operations
        - mysql.connector – For Connecting the Database to do other Operations
        - pandas – For Working Dataframes
        - streamlit – To Build a web app
        - datetime – For Handle the Published Date & Time of the Youtube Vidoes/Comments
        - re – To wrok with the ISO 8601 Format of Duration
   - Set up the YouTube API connection using the provided API key.
     
**2. Functions to Get Data from YouTube API:**
   - Define functions to get channel information, playlist details, video IDs, video information, and comment information from YouTube API.
     
**3. Database Connection and Table Creation,Insertion:**
   - Define the database configuration and create a function to establish a connection to MySQL.
   - Define a function to create tables for storing channel, playlist, video, and comment data in SQL DB.
   - Define functions to insert channel data, playlist data, video data, and comment data into the corresponding tables in the MySQL database.
     
**4.Handling Null / Empty Values:**(if any)
   - This function ensures that the channel and video tables in the database have meaningful default values for descriptions and that there are no null values for Comments Count / Likes Count.
     
**5. Streamlit User Interface:**
   - Set up the Streamlit user interface with a title,header,subheader and sidebar options for selecting the type of data (Channel, Playlists, Videos, Comments, Query Area).
   - Prompt the user to enter a channel ID for data retrieval and display options.
   - Also use some chart to explain the queries that are related to statistic data of the videos 
      (Scatter Chart, Bar Chart, Line Chart, Area Chart)
   - Using Some Status Messages for Providing real-time feedback and progress updates, to keep the client user informed and engaged, leading to a smoother and more intuitive user experience.
     
  **i) Channel Data Retrieval and Storage:**  
     - If "Channel" is selected, fetch and display channel data when the user clicks "Get Data".
     - Store the data to MySQL if the user clicks "Store Data to SQL", checking if the channel data already exists in the database.
    
  **ii) Playlist, Video, and Comment Data Retrieval:**
     - Fetch and display playlist data if "Playlists" is selected.
     - Fetch and display video data if "Videos" is selected.
     - Fetch and display comment data if "Comments" is selected.
    
  **iii) Query Area for Custom Queries:**  
   - Provide a dropdown for the user to select from predefined queries.
   - Execute and display the results of the selected query, such as:
   - All videos and their channel names.
   - Channels with the most number of videos.
   - Top 10 most viewed videos and their channels.
   - Number of comments on each video.
   - Videos with the highest likes and their channel names.
   - Likes and dislikes of all videos.
   - Total views of each channel.
   - Channels that published videos in 2022.
   - Videos with the highest number of comments.
   - All Channels that Stored in a Database with their Basic Details.
------------------------------------------------------------------------------------------------------------
