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

SUMMARY_COLUMN_CONFIG ={
        "Event" : st.column_config.Column(
            "Event",
            width="large"
        )
    }

st.set_page_config(page_title="Timeline Generator",
    page_icon="⏳",
    layout="wide")

# Website header
st.title('Generate a TimeLine! ⏳')

if 'update_summary_key' not in st.session_state:
    st.session_state['update_summary_key'] = False

if 'update_timeline_key' not in st.session_state:
    st.session_state['update_timeline_key'] = False

if 'first_timeline_key' not in st.session_state:
    st.session_state['first_timeline_key'] = True

if 'download_timeline_png_key' not in st.session_state:
    st.session_state['download_timeline_png_key'] = True

topic = st.text_input(label = "", max_chars = 20,help = "Enter a topic for which you need to generate a timeline.")
enter_button = st.button("Generate Timeline!")

if enter_button:
    with st.spinner('Generating Timeline...'):
        #st.write(topic) #comment in production
        summary,wikipedia_link = get_summary(topic)
        #summary = pd.read_pickle(os.path.join(APP_PATH,'data','summary.pkl'))
        summary.columns = ['Date','Event']
        summary['Select'] = True
        st.session_state['wikipedia_link_key'] = wikipedia_link
        st.session_state['update_summary_key'] = True
        st.session_state['summary_key'] = summary

if st.session_state['update_summary_key'] or enter_button:
    left_container, right_container = st.columns(2)
    summary = st.session_state['summary_key']
    st.session_state['update_summary_key'] = True

    with left_container:
        left_left_container,right_left_container = st.columns([0.78,0.22])
        with left_left_container:
            st.write("#### Timeline Data")
            
        with right_left_container:
            download_summary(summary,topic)

        form_data_editor = st.form("data_editor")
        left_left_container,left_right_container = form_data_editor.columns([0.75,0.25])
        
        with left_left_container:
            st.caption(f"Source : {st.session_state['wikipedia_link_key']}")
        with left_right_container:
            update_timeline_button = st.form_submit_button("Update Timeline!",\
                                               help = 'Edit the DataFrame and Click on "Update Timeline" to reflect the changes')

        if enter_button:
            generate_json(summary)
            st.session_state['first_timeline_key'] = False
            
        if update_timeline_button:
            if 'data_editor' in st.session_state:
                data_editor = st.session_state['data_editor']
                edited_rows = data_editor['edited_rows']
                for i,edits in edited_rows.items():
                    for col,val in edits.items():
                        summary.loc[i,col] = val

                st.session_state['summary_key'] = summary
                display_summary = summary[summary.Select]
                generate_json(display_summary)
                
        with right_container:
            html_string = get_timeline_html(topic,st.session_state['download_timeline_png_key'])
            download_timeline() 
            components.html(html_string,scrolling = True,height = 400)
                
        summary = form_data_editor.data_editor(summary,num_rows="dynamic",use_container_width=True,\
                                    key = 'data_editor',column_config = SUMMARY_COLUMN_CONFIG,\
                                 hide_index = True)

st.markdown(
        """
        <style>
        .streamlit-expanderHeader p {
            font-size: 15px;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

with st.expander("Feedback Form"):
    form_feedback = st.form('feedback')
    with form_feedback:
        feedback_title = st.text_input(label = "Title", max_chars = 50)
        feedback_text = st.text_input(label = "Feedback", max_chars = 300)
        feedback_name = st.text_input(label = "Name", max_chars = 50, placeholder = 'Optional')
        feedback_email = st.text_input(label = "Email", max_chars = 100, placeholder = 'Optional')
        print(feedback_title,feedback_text,feedback_name,feedback_email)
        feedback_form_submit = st.form_submit_button("Submit",on_click = save_feedback,args =(feedback_title,feedback_text,feedback_name,feedback_email))
        if feedback_form_submit:
            st.success("Feedback Submitted. Thank you!" ,icon = "✅")
            
        
        
    
    
        
        

    

    
  