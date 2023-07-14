import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import re
sys.path.append(os.path.join(os.getcwd(),"src"))
# sys.path.append("..\src")
from summary_functions import  *
from data_extract import *
import streamlit.components.v1 as components
import json
from streamlit_functions import *
from google.oauth2 import service_account
import gspread

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

FONT_DICT = {
    "Arial": "Arial, sans-serif",
    "Helvetica": "Helvetica, sans-serif",
    "Times New Roman": "Times New Roman, serif",
    "Georgia": "Georgia, serif",
    "Courier New": "Courier New, monospace",
    "Verdana": "Verdana, sans-serif",
    "Trebuchet MS": "Trebuchet MS, sans-serif",
    "Arial Black": "Arial Black, sans-serif",
    "Impact": "Impact, sans-serif",
    "Comic Sans MS": "Comic Sans MS, sans-serif",
    "Palatino": "Palatino, serif",
    "Garamond": "Garamond, serif",
    "Bookman": "Bookman, serif",
    "Arial Narrow": "Arial Narrow, sans-serif",
    "Lucida Console": "Lucida Console, monospace"
}

with open(os.path.join(DATA_PATH,'about.txt')) as about:
    about_str = about.read()

st.set_page_config(page_title="Timeline Generator",
    page_icon="⏳",
    layout="wide",
    menu_items={
        'About': about_str
    })

REVERSE_FONT_DICT = {value:key for key,value in FONT_DICT.items()}

FONT_LIST = tuple(FONT_DICT.keys())
# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)


client = gspread.authorize(credentials)
workbook = client.open("timelineGen")

feedback_sheet = workbook.worksheet('feedback')
gpt_sheet = workbook.worksheet('gpt')

DATA_PATH = os.path.join(os.getcwd(),'data')
APP_PATH = os.getcwd()
MAX_TEXT_CHARS = 48000
SUMMARY_COLUMN_CONFIG ={
        "Event" : st.column_config.Column(
            "Event",
            width="large"
        )
    }

    

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

if 'chatgpt_tokens' not in st.session_state:
    st.session_state['chatgpt_tokens'] = 0

if 'timeline_format_key' not in st.session_state:
    st.session_state['timeline_format_key'] = {
                                                'circle_color':'#7DB46C',
                                                'middle_line_color':'#010101',
                                                'text_box_color':'#ABD6DF',
                                                'background_color':'#E7EBE0',
                                                'font_html':"Comic Sans MS, sans-serif"
                                            }

topic = st.text_input(label = "Enter a Topic or URL", max_chars = 100,help = "Enter a topic for which you need to generate a timeline.")
with st.expander("Or add your own text"):
    topic_text = st.text_area(label = "topic_text",label_visibility = "collapsed", max_chars = 48000, height = 400)

enter_button = st.button("Generate Timeline!")

if enter_button:

    with st.spinner('Generating Timeline...'):
        #st.write(topic) #comment in production
        if len(topic)>0 & len(topic_text) > 0:
            st.warning('As both the topic and user defined text are populated, we use "Enter Topic" text input to fetch topic data and generate the timeline. If you need to use user defined text, delete the text in "Enter Topic" text box ', icon="⚠️")
        if len(topic) > 0:
            summary,source,gpt_metadata = get_summary(topic) 
        else:
            summary,gpt_metadata = get_summary_from_text(topic_text)
            source = "User Text"
            topic = topic_text.split(" ",1)[0]
            topic = re.sub(r"[^a-zA-Z]", "", topic)

        # print(summary)
        gpt_sheet.insert_row(['t_'+topic]+gpt_metadata + [st.session_state['chatgpt_tokens']],2)
        st.session_state['chatgpt_tokens'] = 0
            
        #summary = pd.read_pickle(os.path.join(APP_PATH,'data','summary.pkl'))
        summary['Select'] = True
        st.session_state['source_key'] = source
        st.session_state['topic_key'] = topic
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
            download_summary(summary,st.session_state['topic_key'])

        form_data_editor = st.form("data_editor")
        left_left_container,left_right_container = form_data_editor.columns([0.75,0.25])
        
        with left_left_container:
            st.caption(f"Source : {st.session_state['source_key']}")
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
            with st.expander("Format Timeline"):
                format_timeline = st.form('format_timeline')
                                         
                with format_timeline:
                    circle_color_val,middle_line_color_val,text_box_color_val,background_color_val,font_html\
                    =list(st.session_state['timeline_format_key'].values())
                    circle_color = st.color_picker('Circle Colour', circle_color_val)
                    middle_line_color = st.color_picker('Middle Line Color', middle_line_color_val)
                    text_box_color = st.color_picker('Text Box Color', text_box_color_val)
                    background_color = st.color_picker('Background Color', background_color_val)
                    font_name = REVERSE_FONT_DICT[font_html]
                    font_index = FONT_LIST.index(font_name)
                    font = st.selectbox('Text Font',FONT_LIST,index = font_index)
                    
                    format_timeline_submit = st.form_submit_button('Apply')
                    
                    if format_timeline_submit:
                        font_html = FONT_DICT[font]
                        st.session_state['timeline_format_key'] = {
                                                                    'circle_color':circle_color,
                                                                    'middle_line_color':middle_line_color,
                                                                    'text_box_color':text_box_color,
                                                                    'background_color':background_color,
                                                                    'font_html':font_html
                                                                }

            html_string = get_timeline_html(st.session_state['topic_key'],st.session_state['timeline_format_key'],st.session_state['download_timeline_png_key'])
            download_timeline() 
            components.html(html_string,scrolling = True,height = 400)
                
        summary = form_data_editor\
        .data_editor(summary[['Date','Event','Select']],num_rows="dynamic",use_container_width=True,\
                                    key = 'data_editor',disabled=("Date", "Event"),\
                                    column_config = SUMMARY_COLUMN_CONFIG, hide_index = True)

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
        feedback_title = st.text_input(label = "Title", max_chars = 50,value = "")
        feedback_text = st.text_input(label = "Feedback", max_chars = 300,value = "")
        feedback_name = st.text_input(label = "Name", max_chars = 50, placeholder = 'Optional',value = "")
        feedback_email = st.text_input(label = "Email", max_chars = 100, placeholder = 'Optional',value = "")

        # st.session_state['feedback'] = [feedback_name,feedback_email,feedback_title,feedback_text]
        #print(feedback_title,feedback_text,feedback_name,feedback_email) 
        feedback_form_submit = st.form_submit_button("Submit")
        
        if feedback_form_submit:
            todays_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            feedback = [feedback_name,feedback_email,feedback_title,feedback_text] + [todays_date]
            feedback_sheet.insert_row(feedback, 2)
            st.success("Feedback Submitted. Thank you!" ,icon = "✅")

st.write("---")
markdown_text = '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="https://www.linkedin.com/in/fernandeslloyd/"> Lloyd Fernandes</a> | <a href="https://www.linkedin.com/in/praveen-kumar-murugaiah-843415107/"> Praveen Kumar Murugaiah</a> | <a href="https://www.linkedin.com/in/raunak-sengupta-b62886107/"> Raunak Sengupta</a></h6>'
st.markdown(markdown_text, unsafe_allow_html=True)

         
        
        
    
    
        
        

    

    
  