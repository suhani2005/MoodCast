import csv  # reading and writing csv files
import re   # using regular expressions
import pandas as pd    # data manipulation and analysis
import nltk       # (natural language toolkit) for text processing and analysis
nltk.download('vader_lexicon')   # downloads vader, a dictionary used for sentiment analysis
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import plotly.express as px   # creating interactive visualisations,charts
import plotly.graph_objects as go     # create more customized charts
from colorama import Fore, Style  # allows colored text output
from typing import Dict
import streamlit as st      # used for building interactive webapp


# This function extracts video id
def extract_video_id(youtube_link):
    # this RE matches URL in standard format
    video_id_regex = r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(video_id_regex, youtube_link)
    if match:
        video_id = match.group(1)
        return video_id
    else:
        return None
    
    
# Analyze sentiments
def analyze_sentiment(csv_file):
    # Initialize the sentiment analyzer
    sid = SentimentIntensityAnalyzer()
    comments = []       # initializes an empty list to store comments
    
    # Fixed: Use the correct file handle variable
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Fixed: Use lowercase 'comment' to match what's in your CSV
            comments.append(row['comment'])

    num_neutral = 0
    num_positive = 0
    num_negative = 0
    
    for comment in comments:
        sentiment_scores = sid.polarity_scores(comment)
        
        if sentiment_scores['compound'] == 0.0:
            num_neutral += 1
        # Fixed: Corrected 'compund' to 'compound'
        elif sentiment_scores['compound'] > 0.0:
            num_positive += 1
        else:
            num_negative += 1

    # Fixed: Moved outside the loop
    results = {'num_neutral': num_neutral, 'num_positive': num_positive, 'num_negative': num_negative}
    return results


# Function generates a bar chart to visualize results
def bar_chart(csv_file: str) -> None:
    # call analyze_sentiment function to get results
    results: Dict[str, int] = analyze_sentiment(csv_file)
    num_neutral = results['num_neutral']
    num_positive = results['num_positive']
    num_negative = results['num_negative']

    # create a pandas dataframe with the results
    df = pd.DataFrame({
       'Sentiment': ['Positive', 'Negative', 'Neutral'],
       'Number of Comments': [num_positive, num_negative, num_neutral]
    })

    # create the bar chart using plotly express
    fig = px.bar(df, x='Sentiment', y='Number of Comments', color='Sentiment',
              color_discrete_sequence=['#87CEFA', '#FFA07A', '#D3D3D3'],
              title='Sentiment Analysis Results')
    fig.update_layout(title_font=dict(size=25))
    st.plotly_chart(fig, use_container_width=True)


# function generates a pie chart
def plot_sentiment(csv_file: str) -> None:
    # calls sentiment_analyze function to get results 
    results: Dict[str, int] = analyze_sentiment(csv_file)

    # get counts for each category
    num_neutral = results['num_neutral']
    num_positive = results['num_positive']
    num_negative = results['num_negative']

    # plot the pie chart
    labels = ['Neutral', 'Positive', 'Negative']
    values = [num_neutral, num_positive, num_negative]
    colors = ['yellow', 'green', 'red']
    
    # Fixed: Changed 'value' to 'values' in go.Pie parameters
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent',
                                marker=dict(colors=colors))])
    
    fig.update_layout(title={'text': 'Sentiment Analysis Results', 'font': {'size': 20, 'family': 'Arial', 'color': 'grey'},
                              'x': 0.5, 'y': 0.9},
                      font=dict(size=14))
    
    st.plotly_chart(fig)


# Function to create scatter plot 
def create_scatterplot(csv_file: str, x_column: str, y_column: str) -> None:
    data = pd.read_csv(csv_file)
    fig = px.scatter(data, x=x_column, y=y_column, color='Category')  # this line creates scatter plot using plotly express
    fig.update_layout(
        title='Scatter Plot',
        xaxis_title=x_column,
        # Fixed: Fixed typo in yaxis_title (was yaxistitle)
        yaxis_title=y_column,
        font=dict(size=18)
    )
    st.plotly_chart(fig, use_container_width=True)


def print_sentiment(csv_file: str) -> None:
    results = analyze_sentiment(csv_file)
    num_neutral = results['num_neutral']
    num_positive = results['num_positive']
    num_negative = results['num_negative']

    if num_positive > num_negative:
        overall_sentiment = 'POSITIVE'
        color = Fore.GREEN
    elif num_negative > num_positive:
        overall_sentiment = 'NEGATIVE'
        color = Fore.RED
    else:
        overall_sentiment = 'NEUTRAL'
        color = Fore.YELLOW
        
    print('\n' + Style.BRIGHT + color + overall_sentiment.upper().center(50, ' ') + Style.RESET_ALL)