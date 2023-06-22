import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
sys.path.append("..\src")
sys.path.append("\src")
from summary_functions import  *
from streamlit_functions import *
from data_extract import *
import streamlit.components.v1 as components
import json

DATA_PATH = os.path.join(os.getcwd(),'data')

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

def get_summary(topic):
    
    wikipedia_link = google_search_link(topic)
    if wikipedia_link == "NONE":
        st.write("No Input Given")
        return None
        
    else:
        #st.write(f"Data fetched from {wikipedia_link}")
        text = get_wikipedia_text(wikipedia_link)
        summary = summarize_text(text)
        return summary

# def get_timeline_html(topic):
#     with open('timeline_display.html','w') as file:
#         file.truncate()
#         with open('template_p1.txt') as p1:
#             p1_str = p1.read()
#             p1_str = p1_str.replace('&&&&&&&&name&&&&&&&',topic)
#             file.write(p1_str)
#         with open('events.json','r') as p2:
#             events = json.load(p2)
#             file.write(json.dumps(events))
#         with open('template_p2.txt','r') as p3:
#             file.write(p3.read())

#     with open('timeline_display.html','r') as s:
#         html_string = s.read()
#     return html_string

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
    
def generate_timeline(topic,right_container):
    html_string = get_timeline_html(topic,st.session_state['download_timeline_png_key'])
    with right_container:
        right_left_container,right_right_container = st.columns([0.7,0.3])

        with right_left_container:
            update_timeline_button = st.button("Update Timeline!",on_click = update_timeline_change,\
                                               help = 'Edit the DataFrame and Click on "Update Timeline" to reflect the changes')

        with right_right_container:
            download_timeline_button = st.button("Download Timeline!",on_click = update_download_timeline_png_change,\
                                                 help = 'Download timeline in .png form')
            
        components.html(html_string,scrolling = True,height = 400)

def update_summary_change(): 

    if 'data_editor' in st.session_state:
        st.session_state['update_summary_key'] = True
        summary = st.session_state['summary_key']
        data_editor = st.session_state['data_editor']
        edited_rows = data_editor['edited_rows']
        
        for i,edits in edited_rows.items():
            for col,val in edits.items():
                summary.loc[i,col] = val
        st.session_state['summary'] = summary

def update_timeline_change():
    st.session_state['update_timeline_key'] = True

# st.write(st.session_state)
