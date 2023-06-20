import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
sys.path.append("..\src")
sys.path.append("src")
from summary_functions import  *
from data_extract import *
import streamlit.components.v1 as components
import json
from streamlit_functions import *

APP_PATH = os.getcwd()

st.set_page_config(page_title="Timeline Generator",
    page_icon="⏳",
    layout="wide")

# Website header
st.title('Generate a TimeLine! ⏳')
st.divider()
st.subheader('Enter the Topic below 👇')

# st.write(st.session_state)

if 'update_summary_key' not in st.session_state:
    st.session_state['update_summary_key'] = False

if 'update_timeline_key' not in st.session_state:
    st.session_state['update_timeline_key'] = False

if 'first_timeline_key' not in st.session_state:
    st.session_state['first_timeline_key'] = True

topic = st.text_input(label = "", max_chars = 20,help = "Enter a topic for which you need to generate a timeline.")
enter_button = st.button("Generate Timeline!")

if enter_button:
    #st.write(topic) #comment in production
    summary = get_summary(topic)
    #summary = pd.read_pickle(os.path.join(APP_PATH,'data','summary.pkl'))
    summary.columns = ['Date','Event']
    summary['Select'] = True
    st.session_state['update_summary_key'] = True
    st.session_state['summary_key'] = summary

if st.session_state['update_summary_key'] or enter_button:
    left_container, right_container = st.columns(2)
    summary = st.session_state['summary_key']
    # st.write(summary)

    summary_column_config={
        "Event" : st.column_config.Column(
            "Event",
            width="large"
        )
    }
    
    with left_container:
        left_left_container,right_left_container = st.columns([0.78,0.22])
        with left_left_container:
            st.write("#### Timeline Data")
        with right_left_container:
            download_summary(summary,topic)
        summary = st.data_editor(summary,num_rows="dynamic",use_container_width=True,\
                                    key = 'data_editor',column_config = summary_column_config,\
                                 hide_index = True,on_change = update_summary_change)
        
    # st.write(summary)
    st.session_state['summary_key'] = summary
    
    if st.session_state['first_timeline_key']:
        generate_json(summary)
        st.session_state['first_timeline_key'] = False
     
    if st.session_state['update_timeline_key']:
        print("Updating timeline")
        display_summary = summary[summary.Select]
        generate_json(display_summary)
        st.session_state['update_timeline_key'] = False

    generate_timeline(topic,right_container)

# st.write(st.session_state)   


    

        
      