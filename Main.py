import streamlit as st
import Functions as fun
import pandas as pd

conn = fun.create_connection()
fun.create_tables(conn)

#STREAMLIT APP
st.set_page_config(page_icon=r"D:\CAPSTONE\youtube\IMAGES\logo.png",page_title="YouTube Data Insights",layout='wide')
st.title(":black[YOUTUBE DATA HARVESTING AND WAREHOUSING]")
db,arr,war = st.columns(3)
with db:
    st.image(r"D:\CAPSTONE\youtube\IMAGES\database.jpg")
with arr:
    st.image(r"D:\CAPSTONE\youtube\IMAGES\connect.jpg")
with war:
    st.image(r"D:\CAPSTONE\youtube\IMAGES\extract.jpg")
st.subheader('''Explore and Analyze Data from Multiple YouTube Channels with Our Interactive Web Application''')
selected_option = st.sidebar.radio("Data About..", ["CHANNEL", "PLAYLISTS", "VIDEOS", "COMMENTS","QUERY AREA"])
#CHANNEL PAGE
if selected_option == "CHANNEL":
    st.markdown("<p style='font-size:20px;'>Enter a YouTube Channel ID to Access Comprehensive Information such as:<b> Channel Name | Subscribers Count | Total Videos Count</b></p>", unsafe_allow_html=True)
    channel_id = st.text_input('', placeholder="Here..")
    if channel_id:
        st.subheader("""You can View the Data about a Channel by Clicking Below.""")
        #DATA RETRIVAL BUTTON
        if st.button("**_Get Data_**"):
            try:
                df = fun.get_channel_info(channel_id)
                df = pd.DataFrame([df])
                st.info("Here it Comes..")
                st.dataframe(df,use_container_width = True)
            except KeyError:
                st.error("Please Provide a Valid YouTube Channel ID")
        st.subheader("""You can Store All the Data into a Database by Clicking Below.""")
        #STORE BUTTON
        if st.button("**_Store All Data to SQL_**"):
            conn = fun.create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Channel_Id FROM channel WHERE Channel_Id = %s", (channel_id,))
            existing_channel = cursor.fetchone()
            cursor.execute("SELECT Video_Id FROM video WHERE Video_Id = %s", (channel_id,))
            existing_video = cursor.fetchone()
            cursor.execute("SELECT Playlist_Id FROM playlist WHERE Playlist_Id = %s", (channel_id,))
            existing_playlist = cursor.fetchone()
            if existing_channel:
                st.warning("Channel details of the given channel ID already exist")
            else:
                channel_data = fun.get_channel_info(channel_id)
                fun.insert_channel_data(conn, channel_data)
                playlist_data = fun.get_playlist_details(channel_id)
                fun.insert_playlist_data(conn, playlist_data)
                for playlist in playlist_data:
                    cursor.execute("SELECT Playlist_Id FROM playlist WHERE Playlist_Id = %s", (playlist['Playlist_Id'],))
                    if not cursor.fetchone():
                        st.warning(f"Playlist Id {playlist['Playlist_Id']} could not be inserted")
                        break
                video_ids  = fun.get_videos_ids(channel_id)
                video_data = fun.get_video_info(video_ids, channel_id)
                fun.insert_video_data(conn, video_data)
                cursor.execute("SELECT Comment_Id FROM comment WHERE Comment_Id = %s", (channel_id,))
                existing_comment = cursor.fetchone()           
                comment_data = fun.get_comment_info(video_ids)
                fun.insert_comment_data(conn, comment_data)
                st.success("Data inserted successfully")
                fun.update_null_values(conn)
#PLAYLIST PAGE
elif selected_option == "PLAYLISTS":
    st.markdown("""<p style='font-size:20px;'>Enter a YouTube Channel ID to Access Comprehensive Information such as: <b>Playlist Name</b></p>""", unsafe_allow_html=True)
    channel_id = st.text_input('', placeholder="Here..")
    if channel_id:
        st.subheader("""You can View the Data about a Playlist of the Channel by Clicking Below.""")
        if st.button("**_Get Data_**"):
            df1 = fun.get_playlist_details(channel_id)
            df1 = pd.DataFrame(df1)
            st.info("Here it Comes..")
            st.dataframe(df1,use_container_width = True)
            len = len(df1)
            st.success(f"There are {len} Playlists in this Channel")
#VIDEOS PAGE
elif selected_option == "VIDEOS":
    st.markdown( """<p style='font-size:20px;'>Enter a YouTube Channel ID to Access Comprehensive Information such as:<b> Video name | Likes | Dislikes | Comments | Duration | Thumbnails | more..</b></p>""",unsafe_allow_html=True)
    channel_id = st.text_input('', placeholder="Here..")
    if channel_id:
        st.subheader("""You can View the Data about a Videos of the Channel by Clicking Below.""")
        if st.button("**_Get Data_**"):
            video_ids = fun.get_videos_ids(channel_id)
            video_data = fun.get_video_info(video_ids,channel_id)
            df2 = pd.DataFrame(video_data)
            st.info("Here it Comes..")
            st.dataframe(df2,use_container_width=True)
            len = len(df2)
            st.success(f"There are {len} Videos in this Channel")
            def convert_to_minutes(time_str):
                h, m, s = map(int, time_str.split(':'))
                return h * 60 + m + s / 60
            df2['Duration'] = df2['Duration'].apply(convert_to_minutes)
            average_duration = df2['Duration'].mean()
            st.success(f"The average duration of all videos in this channel is {average_duration:.2f} minutes")

#COMMENTS PAGE
elif selected_option == "COMMENTS":
    st.markdown("""<p style='font-size:20px;'>Enter a YouTube Channel ID to Access Comprehensive Information such as: <b>Comment Author | Comment Text | Published Date</b></p>""", unsafe_allow_html=True)
    channel_id = st.text_input('', placeholder="Here..")
    if channel_id:
        st.subheader("""You can View the Data about a Comments of all the Videos in the Channel by Clicking Below.""")
        if st.button("**_Get Data_**"):
            video_ids = fun.get_videos_ids(channel_id)
            comment_data = fun.get_comment_info(video_ids)
            df3 = pd.DataFrame(comment_data)
            st.info("Here it Comes..")
            st.dataframe(df3,use_container_width=True)
            len = len(df3)
            st.success(f"There are {len} Comments in this Channel")
#QUERY PAGE
elif selected_option == "QUERY AREA":
    st.markdown("""<p style='font-size:20px;'>You Can View Some of the Queries About the Stored Channel Here </p>""",unsafe_allow_html=True)   
    QUERIES=st.selectbox( ' ',("Choose a Query",
                                            "1. All the Videos and their Channel Name",
                                            "2. Channels with Most Number of Videos and thier Count",
                                            "3. Top 10 Most viewed videos and their Channels",
                                            "4. Number of Comments in Each Videos",
                                            "5. Videos with higest likes and thier Channel Name",
                                            "6. Likes of All Videos",
                                            "7. Toatl Views of Each Channel",
                                            "8. Channels that have Published Videos in the year of 2022",
                                            "9. Average Duration of All Videos in Each Channel",
                                            "10. Videos with Highest Number of Comments",
                                            "11. All Channels in the Database",
    ))

    if QUERIES != 'Choose a Query':          
        if QUERIES=="1. All the Videos and their Channel Name":
            query1='''select  a.channel_Name,c.video_name from channel as a join playlist as b
                on a.channel_id=b.channel_id inner join video as c 
                on b.playlist_Id = c.Playlist_Id'''
            conn = fun.create_connection()
            cursor = conn.cursor()
            cursor.execute(query1)
            t1=cursor.fetchall()
            df=pd.DataFrame(t1,columns=["Channel Name","Video Name"])
            st.dataframe(df,use_container_width=True)
        elif QUERIES=="2. Channels with Most Number of Videos and thier Count":
            query2='''select channel_name ,Videos_Count
            from channel 
            order by Videos_Count desc limit 4'''
            conn = fun.create_connection()
            cursor = conn.cursor()
            cursor.execute(query2)
            t2=cursor.fetchall()
            df2=pd.DataFrame(t2,columns=["Channel Name","Videos Count"])
            st.dataframe(df2,use_container_width=True)
            st.bar_chart(df2.set_index('Channel Name'),color=[])
        elif QUERIES=="3. Top 10 Most viewed videos and their Channels":
            query3='''SELECT a.Video_Name, c.channel_name ,a.Views_Count
                        FROM video AS a JOIN playlist AS b 
                        ON a.playlist_Id = b.playlist_Id
                        JOIN channel AS c ON b.channel_id = c.channel_id 
                        ORDER BY a.Views_Count DESC LIMIT 10;'''
            conn = fun.create_connection()
            cursor = conn.cursor()
            cursor.execute(query3)
            t3=cursor.fetchall()
            df3=pd.DataFrame(t3,columns=["Video_Name","Channel Name","Views_Count"])
            st.dataframe(df3,use_container_width=True)
            st.bar_chart(df3, y='Views_Count',x ='Video_Name', use_container_width=True,height=500,color="#B3009B")
        elif QUERIES=="4. Number of Comments in Each Videos":
            query4='''select Video_Name,Comments_Count from video order by Comments_Count desc '''
            conn = fun.create_connection()
            cursor = conn.cursor()
            cursor.execute(query4)
            t4=cursor.fetchall()
            df4=pd.DataFrame(t4,columns=["Video_Name","No. of Comments"])
            st.dataframe(df4,use_container_width=True)
        elif QUERIES=="5. Videos with higest likes and thier Channel Name":
            query5='''SELECT c.video_name, a.channel_Name, c.Likes_Count FROM channel AS a
                    JOIN playlist AS b ON a.channel_id = b.channel_id
                    INNER JOIN video AS c ON b.playlist_Id = c.playlist_Id
                    ORDER BY c.Likes_Count DESC
                    LIMIT 10'''
            conn = fun.create_connection()
            cursor = conn.cursor()
            cursor.execute(query5)
            t5=cursor.fetchall()
            df5=pd.DataFrame(t5,columns=["Video Names","Channel Name","Likes Count"])
            st.dataframe(df5,use_container_width=True)
            st.line_chart(df5,x="Video Names",y=["Channel Name","Likes Count"], color=["#B3009B", "#620A56"])
        elif QUERIES=="6. Likes of All Videos":
            query6='''select Video_Name, Likes_Count from video ORDER BY Likes_Count DESC'''
            conn = fun.create_connection()
            cursor = conn.cursor()
            cursor.execute(query6)
            t6=cursor.fetchall()
            df6=pd.DataFrame(t6,columns=["Video Names","Likes_Count"])
            st.dataframe(df6,use_container_width=True)
        elif QUERIES=="7. Toatl Views of Each Channel":
            query7='''select Channel_Name,views_Count  from channel ORDER BY views_Count DESC'''
            conn = fun.create_connection()
            cursor = conn.cursor()
            cursor.execute(query7)
            t7=cursor.fetchall()
            df7=pd.DataFrame(t7,columns=["Channel Name","TotalViews"])
            st.dataframe(df7,use_container_width=True)
            st.scatter_chart(df7,y='Channel Name',x='TotalViews',color="#B3009B",size=700,use_container_width=True,height=500)
        elif QUERIES=="8. Channels that have Published Videos in the year of 2022":
            query8='''SELECT DISTINCT a.channel_name
                        FROM channel AS a
                        JOIN playlist AS b ON a.channel_id = b.channel_id
                        INNER JOIN video AS c ON b.playlist_Id = c.playlist_Id
                        WHERE EXTRACT(YEAR FROM c.Published_Date) = 2022'''
            conn = fun.create_connection()
            cursor = conn.cursor()
            cursor.execute(query8)
            t8=cursor.fetchall()
            df8=pd.DataFrame(t8,columns=["Channel name"])
            st.dataframe(df8,use_container_width=True)
        elif QUERIES=="9. Average Duration of All Videos in Each Channel":
            query9='''  SELECT a.channel_name AS "Channel Name", 
                        SEC_TO_TIME(AVG(TIME_TO_SEC(c.duration))) AS "Average Duration"
                        FROM channel AS a 
                        JOIN playlist AS b ON a.channel_id = b.channel_id
                        INNER JOIN video AS c ON b.playlist_id = c.playlist_id
                        GROUP BY a.channel_name'''
            conn = fun.create_connection()
            cursor = conn.cursor()
            cursor.execute(query9)
            t9=cursor.fetchall()
            df9=pd.DataFrame(t9,columns=["Channel Name","Average Duration"])
            st.dataframe(df9,use_container_width=True)
        elif QUERIES=="10. Videos with Highest Number of Comments":
            query10='''SELECT c.Video_Name,a.channel_name,c.Comments_Count
                        FROM channel AS a
                        JOIN playlist AS b ON a.channel_id = b.channel_id
                        INNER JOIN video AS c ON b.playlist_Id = c.playlist_Id
                        order by Comments_Count desc limit 8;'''
            conn = fun.create_connection()
            cursor = conn.cursor()
            cursor.execute(query10)
            t10=cursor.fetchall()
            df10=pd.DataFrame(t10,columns=["Video Name","Channel Name","Comments Count"])
            st.dataframe(df10,use_container_width=True)
        elif QUERIES=="11. All Channels in the Database":
            query11='''SELECT * FROM channel ORDER BY Subscribers_Count DESC'''
            conn = fun.create_connection()
            cursor = conn.cursor()
            cursor.execute(query11)
            t11=cursor.fetchall()
            df11=pd.DataFrame(t11,columns=["Channel ID","Channel Name","Description","Subscriber Count","View Count","Video Count"])
            st.dataframe(df11,use_container_width=True)
            st.info(f"There are {len(df11)} Channels in the Database")
        cursor.close()
conn.close()    