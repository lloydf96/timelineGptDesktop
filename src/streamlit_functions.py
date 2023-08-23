# -*- coding: utf-8 -*-
"""streamlit_functions.py

Created by Lloyd Fernandes, https://github.com/lloydf96?tab=repositories

"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
sys.path.append("..\src")
from summary_functions import  *
from data_extract import *
import streamlit.components.v1 as components
import json
from datetime import datetime
import time

#get path to all the data stored
DATA_PATH = os.path.join(os.getcwd(),'data')


def get_timeline_html(topic,format,download):
    '''
    It generates html string to get the timeline plot.

    Input:
    topic : topic name to get name for the downloaded image file
    format: format options to change color font
    download : Whether to download the image or not
    '''
    
    #if no download, download is false
    if download:

        #write in the html file
        with open(os.path.join(DATA_PATH,'timeline_display.html'),'w') as file:
            file.truncate()
            with open(os.path.join(DATA_PATH,'template_p1.txt')) as p1:

                #update at different locations in the string to get desired font
                p1_str = p1.read()
                p1_str = p1_str.replace('&&&&&&&&name&&&&&&&',topic)
                p1_str = p1_str.replace('&&&&&&&&circlecolor&&&&&&&',format['circle_color'])
                p1_str = p1_str.replace('&&&&&&&&middlelinecolor&&&&&&&',format['middle_line_color'])
                p1_str = p1_str.replace('&&&&&&&&textboxcolor&&&&&&&',format['text_box_color'])
                p1_str = p1_str.replace('&&&&&&&&backgroundcolor&&&&&&&',format['background_color'])
                p1_str = p1_str.replace('&&&&&&&&font&&&&&&&',format['font_html'])
                file.write(p1_str)
                
            with open(os.path.join(DATA_PATH,'events.json'),'r') as p2:
                #append the events.json to the string
                events = json.load(p2)
                file.write(json.dumps(events))
                
            with open(os.path.join(DATA_PATH,'template_p2.txt'),'r') as p3:
                #append the rest of the string 
                file.write(p3.read())

        #read the html file with updated format
        with open(os.path.join(DATA_PATH,'timeline_display.html'),'r') as s:
            html_string = s.read()
        return html_string

    else:
        with open(os.path.join(DATA_PATH,'timeline_display.html'),'w') as file:
            file.truncate()
            
            with open(os.path.join(DATA_PATH,'template_p1_download.txt')) as p1:
                #update at different locations in the string to get desired font
                #the template_p1_download.txt has the javascript function for downloading the html as a png.
                p1_str = p1.read()
                p1_str = p1_str.replace('&&&&&&&&name&&&&&&&',topic)
                p1_str = p1_str.replace('&&&&&&&&circlecolor&&&&&&&',format['circle_color'])
                p1_str = p1_str.replace('&&&&&&&&middlelinecolor&&&&&&&',format['middle_line_color'])
                p1_str = p1_str.replace('&&&&&&&&textboxcolor&&&&&&&',format['text_box_color'])
                p1_str = p1_str.replace('&&&&&&&&backgroundcolor&&&&&&&',format['background_color'])
                p1_str = p1_str.replace('&&&&&&&&font&&&&&&&',format['font_html'])
                file.write(p1_str)
                
            with open(os.path.join(DATA_PATH,'events.json'),'r') as p2:
                #append the events.json to the string
                events = json.load(p2)
                file.write(json.dumps(events))
                
            with open(os.path.join(DATA_PATH,'template_p2.txt'),'r') as p3:
                #append the rest of the string 
                file.write(p3.read())
                
        #read the html file with updated format
        with open(os.path.join(DATA_PATH,'timeline_display.html'),'r') as s:
            html_string = s.read()

        #update the download session state back to original
        st.session_state['download_timeline_png_key'] = True
        return html_string

        
#function is cached to prevent repeated chatgpt api call for same topic
@st.cache_data(show_spinner=False)
def get_summary(topic):
    '''
    Get summary given the input topic
    '''
    #check if the url is valid
    text,link_flag = validate_url(topic)
    
    #if it is invalid, then the text would be a topic
    #in this case we need to search for the topic in wikipedia
    if link_flag == 'Invalid Link':
        wikipedia_link = get_wiki_link(topic)
        if wikipedia_link == "NONE":
            st.write("No Input Given")
            return None
        else:
            #get text from wikipedia
            text = get_wikipedia_text(wikipedia_link)
            link = wikipedia_link
    else:
        link = topic
    summary,gpt_metadata = summarize_text(text)
   
    return summary,link,gpt_metadata

    
#function is cached to prevent repeated chatgpt api call for same text
@st.cache_data(show_spinner=False)
def get_summary_from_text(text):
    '''
    Get summary given text
    '''
    summary,gpt_metadata = summarize_text(text)
    return summary,gpt_metadata


def download_summary(summary,topic):
    '''
    Add a download button and download as csv if clicked.
    '''
    download_summary_df = summary[['Order','Date','Event','Select']]
    st.download_button(
        label="Download CSV",
        data = download_summary_df.to_csv().encode('utf-8'),
        file_name=f'summary_{topic}.csv',
        mime='text/csv'
    )


def generate_json(df):
    '''
    Generate json file from dataframe. json file contains just the date and event
    '''
    df_dict = dict(zip(*[df.Date,df.Event]))
    df_dict = [{"date" : date,"event":event} for date,event in df_dict.items()]
    with open(os.path.join(DATA_PATH,'events.json'), 'w') as f:
        json.dump(df_dict, f)


def update_download_timeline_png_change():
    '''
    Changes the flag which triggers download of timeline plot
    '''
    st.session_state['download_timeline_png_key'] = False


def download_timeline():
    '''
    get timeline image download button
    '''
    download_timeline_button = st.button("Download Timeline!",on_click = update_download_timeline_png_change,\
                                             help = 'Download timeline in .png form')



