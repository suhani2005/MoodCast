import streamlit as st
import os
from senti import extract_video_id, analyze_sentiment, bar_chart, plot_sentiment
from scraper import save_comments, get_channel_info, youtube, get_channel_id, get_video_stats

#(fun)deletes csv file in the specified directory that does not match current videos ID
def delete_non_matching_csv_files(directory_path, video_id):
    for file_name in os.listdir(directory_path):  #lists all the files in the directory
        if not file_name.endswith('.csv'):   #skips files without .csv extension
            continue
        if file_name == f'{video_id}.csv':   #skips file that matches current video ID
            continue
        os.remove(os.path.join(directory_path, file_name))  #deletes file that doesnt match current video ID


#configures streamlit page settings
st.set_page_config(page_title='Suhani_Negi', page_icon='pic.png', initial_sidebar_state='auto')
st.sidebar.title("Sentimental Analysis") #sets title of sidebar
st.sidebar.header("Enter Youtube Link")  #adds header in the sidebar prompting user to enter a link
youtube_link = st.sidebar.text_input("Link") #creates a text  input field in sidebar

directory_path = os.getcwd() #gets current working directory


#custom CSS to hide the default Streamlit menu and footer elements from app interface
hide_st_style = """  
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True) #injects custom CSS to app


# Main Logic when link is provided
video_id = None  # Set default value for video_id

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        channel_id = get_channel_id(video_id)

if video_id:  # If a valid video is extracted
    st.sidebar.write("The Video is: ", video_id)  # Displays video in the sidebar
    csv_file = save_comments(video_id)  # Saves the comments of video in a csv file and stores file path
    delete_non_matching_csv_files(directory_path, video_id)  # Deletes any non-matching csv file
    st.sidebar.write("Comments saved to CSV!")  # Shows a message indicating comments have been saved 

    # Creates a download button in the sidebar that allows user to download the comments csv file
    st.sidebar.download_button(label="Download Comments", data=open(csv_file, 'rb').read(), file_name=os.path.basename(csv_file), mime="text/csv")


# Fetch and display channel info if video_id is valid
if video_id:
    channel_info = get_channel_info(youtube, channel_id)  # Fetches channel info

    col1, col2 = st.columns(2)  # Creates a 2-column layout for displaying channel logo and title

    with col1:
        channel_logo_url = channel_info['channel_logo_url']
        st.image(channel_logo_url, width=250)

    with col2:
        channel_title = channel_info['channel_title']
        st.title(' ')
        st.text("Youtube channel name")
        st.title(channel_title)


    # Channel stats
    st.title(" ")
    col3, col4, col5 = st.columns(3)  # Creates a 3-column layout

    with col3:
        video_count = channel_info['video_count']
        st.header("Total Videos")
        st.subheader(video_count)

    with col4:
        channel_created_date = channel_info['channel_created_date']
        created_date = channel_created_date[:10]
        st.header("Channel Created")
        st.subheader(created_date)

    with col5:
        st.header("Subscriber Count")
        st.subheader(channel_info["subscriber_count"])


    # Displays video stats
    stats = get_video_stats(video_id)  # Fetches video stats

    st.title("Video Information: ")
    col6, col7, col8 = st.columns(3)

    with col6:
        st.header("Total Views")
        st.subheader(stats["viewCount"])

    with col7:
        st.header("Like Count")
        st.subheader(stats["likeCount"])

    with col8:
        st.header("Comment Count")
        st.subheader(stats["commentCount"])


    # Video Playback
    _, container, _ = st.columns([10, 80, 10])
    container.video(data=youtube_link)  # Displays the video directly in the app using provided link


    # Sentiment Analysis Results
    results = analyze_sentiment(csv_file)

    col9, col10, col11 = st.columns(3)

    with col9:
        st.header("Positive Comments ")
        st.subheader(results['num_positive'])

    with col10:
        st.header("Negative Comments ")
        st.subheader(results['num_negative'])

    with col11:
        st.header("Neutral Comments ")
        st.subheader(results['num_neutral'])


    # Visualizing Sentiment
    bar_chart(csv_file)
    plot_sentiment(csv_file)


    # Channel Description
    st.subheader("Channel Description ")
    channel_description = channel_info['channel_description']
    st.write(channel_description)  # Displays the description fetched earlier


# Error Handling
else:
    st.error("Invalid Youtube Link or Video ID not found")

