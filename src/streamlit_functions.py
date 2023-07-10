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

DATA_PATH = os.path.join(os.getcwd(),'data')
FEEDBACK_PATH = os.path.join(os.getcwd(),"data","feedback","feedback.csv")

def get_timeline_html(topic,download):
    if download:
        with open(os.path.join(DATA_PATH,'timeline_display.html'),'w') as file:
            file.truncate()
            with open(os.path.join(DATA_PATH,'template_p1.txt')) as p1:
                p1_str = p1.read()
                p1_str = p1_str.replace('&&&&&&&&name&&&&&&&',topic)
                file.write(p1_str)
            with open(os.path.join(DATA_PATH,'events.json'),'r') as p2:
                events = json.load(p2)
                file.write(json.dumps(events))
            with open(os.path.join(DATA_PATH,'template_p2.txt'),'r') as p3:
                file.write(p3.read())
    
        with open(os.path.join(DATA_PATH,'timeline_display.html'),'r') as s:
            html_string = s.read()
        return html_string

    else:
        with open(os.path.join(DATA_PATH,'timeline_display.html'),'w') as file:
            file.truncate()
            with open(os.path.join(DATA_PATH,'template_p1_download.txt')) as p1:
                p1_str = p1.read()
                p1_str = p1_str.replace('&&&&&&&&name&&&&&&&',topic)
                file.write(p1_str)
            with open(os.path.join(DATA_PATH,'events.json'),'r') as p2:
                events = json.load(p2)
                file.write(json.dumps(events))
            with open(os.path.join(DATA_PATH,'template_p2.txt'),'r') as p3:
                file.write(p3.read())
    
        with open(os.path.join(DATA_PATH,'timeline_display.html'),'r') as s:
            html_string = s.read()
        st.session_state['download_timeline_png_key'] = True
        return html_string

@st.cache_data(show_spinner=False)
def get_summary(topic):
    
    wikipedia_link = get_wiki_link(topic)
    if wikipedia_link == "NONE":
        st.write("No Input Given")
        return None
        
    else:
        #st.write(f"Data fetched from {wikipedia_link}")
        text = get_wikipedia_text(wikipedia_link)
        summary = summarize_text(text)
        return summary,wikipedia_link


@st.cache_data(show_spinner=False)
def get_summary_from_text(text):
    summary = summarize_text(text)
    return summary

def download_summary(summary,topic):
    
    st.download_button(
        label="Download CSV",
        data=summary.to_csv().encode('utf-8'),
        file_name=f'summary_{topic}.csv',
        mime='text/csv'
    )

def generate_json(df):
    df_dict = dict(zip(*[df.Date,df.Event]))
    df_dict = [{"date" : date,"event":event} for date,event in df_dict.items()]
    with open(os.path.join(DATA_PATH,'events.json'), 'w') as f:
        json.dump(df_dict, f)

def update_download_timeline_png_change():
    st.session_state['download_timeline_png_key'] = False

def download_timeline():
    
    download_timeline_button = st.button("Download Timeline!",on_click = update_download_timeline_png_change,\
                                             help = 'Download timeline in .png form')

def save_feedback(feedback_title,feedback_text,feedback_name,feedback_email,sheet):
    # table_name = st.secrets["private_gsheets_url"]
    todays_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    feedback = st.session_state['feedback'] + [todays_date]
    sheet.insert_row(feedback, 2)
    # query = f'INSERT INTO "{table_name}" VALUES ("abc","","","","2023-10-09")'
    # print(query)
    # connection.execute(query)
    

