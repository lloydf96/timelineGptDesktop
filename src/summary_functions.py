# -*- coding: utf-8 -*-
"""summary_functions.py

Created by Lloyd Fernandes, https://github.com/lloydf96?tab=repositories
and Praveen Kumar Murugaiah, parveen00@gmail.com

"""

import requests
import random
from langchain.text_splitter import CharacterTextSplitter
import tiktoken
import pandas as pd
import openai
import ast
import re
import os
import streamlit as st
import time
from datetime import datetime

#define all global variables
ENCODING_NAME = "gpt-3.5-turbo"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 50
MAX_CHUNKS = 10
MAX_WORDS = 4000
BULLET_SIGN = '->'

#get the list of available api_keys and get one at random.
#This was done for load balancing
API_KEY = st.secrets['chatgpt_api']
openai.api_key = API_KEY
ERROR_LOG_FOLDER = os.getcwd()


def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(ENCODING_NAME)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def get_chunks(text,chunk_size = CHUNK_SIZE,chunk_overlap = CHUNK_OVERLAP):
    '''
    Split a single document into multiple chunks of size less than CHUNK_SIZE and overlap
    of CHUNK_OVERLAP.
    The chunking is done with a "." seperator
    '''
    
    assert type(text) == str, "text file is not of type string recheck"

    #get total number of words and enforce word limit
    list_of_words = text.split()
    text = ' '.join(list_of_words[:MAX_WORDS])

    #split text into small chunks
    text_splitter = CharacterTextSplitter(        
        separator = ". ",
        chunk_size = chunk_size,
        chunk_overlap  = chunk_overlap,
        length_function = num_tokens_from_string,
    )

    #add full stop in end
    text_list = [x + "." for x in text_splitter.split_text(text)]

    #enforce chunk limit
    if len(text_list) > MAX_CHUNKS:
        text_list = text_list[:MAX_CHUNKS]
        
    return text_list


def content_moderation_api(text):
    '''
    Check if text follows openai content moderation guidelines
    '''
    response = openai.Moderation.create(
    input=text
)
    output = response["results"][0].flagged
    return output


def content_moderation(text_list):
    '''
    Detect if the text chunks have any content violating openai guidelines. If so return True
    '''
    for text in text_list:
        response = content_moderation_api(text)
        if response:
            return True

    return False


def get_summary(text):
    '''
    Get summary from chatGPT from a text input
    '''
    #replace Bullet sign with no space, to make sure that the prompt is not confusing
    text = text.replace(BULLET_SIGN,"")

    #run API with the prompt and text chunk
    result = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are an extractive summarizer"},
            {"role": "user", "content": f"For the text which begins after the symbol '*****', please extract all events along with their date. Begin" +\
             f" the bullet points with '{BULLET_SIGN}' and separate date and event with ':'. Each event list should begin with the date followed by the event description. \n\n Text '*****'  {text}"}
        ],temperature = 0)

    #get the result
    response = result.choices[0].message.content
    if "\n\n" in response:
        response = response.split("\n\n")[1]

    #get total number of chatgpt tokens (just for chatgpt usage information)
    total_tokens = str(result.usage.total_tokens)
    return response,total_tokens


def get_list_of_summary(text_list):
    '''
    Get list of summaries from list of text chunks
    '''
    #get list of summaries
    summary_list = [get_summary(text) for text in text_list]

    #get list of total number of tokens used along with the summary as seperate list
    token_list = [i[1] for i in summary_list]
    summary_list = [i[0] for i in summary_list]
 
    #split each summary into list
    summary_list = [summary.split(BULLET_SIGN) for summary in summary_list]
    
    #convert list of list into a single list
    summary_list = [event for sublist in summary_list for event in sublist]

    return summary_list,token_list


def process_summary(summary_list):
    '''
    Edit list of summary
    '''
    
    #keep events which have colon in between
    summary_list = [event for event in summary_list if ':' in event]

    #split date:event into date,event
    summary_list = [event.split(':',1) for event in summary_list]

    #remove empty events
    summary_list = [event for event in summary_list if len(event[0])>0]
 
    #remove \n in event description
    summary_list = [[date,event.replace('\n','')] for [date,event] in summary_list]

    return summary_list


def isBC(x):
    'return negative if BC in x'
    try:
        if 'BC' in x:
            return -1
        else:
            return 0
    except:
        return 0


def get_approx_month_year(df):
    #get list of dates
    list_of_dates = df['Date'].tolist()
    #run the list of dates through chatgpt to get the output as an approximate month and year
    result = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a function that gives a single month year approximation for a list of phrases"},
            {"role": "user", "content":  f'''for the list of phrase give a list of month year approximation {list_of_dates}. Format the list as follows: If spans across centuries, give a single representative month and year that lies in the period. Give the output in the format <input phrase>-><output month> <output year along with BC or AD time system>. If <output year> > 10000, give 10000. Give each element of the list one below the other.'''}
        ],temperature = 0)

    response = result.choices[0].message.content

    if "\n\n" in response:
        response = response.split("\n\n")[1]

    dates = response.split('\n')

    #get a mapping of the date input with the month year approximation
    date_mapper = dict()
    for date in dates:

        key, value = date.split('->')
        key =  key.strip()
        value =  value.strip()
        
        # Check chatGPI returns None when there is year in the input data
        # If yes, get the year and add 'January' as default month
        # If No, then skip this process
        
        if value == 'None':
            year = re.search(f'[0-9].*', value)
            if year == None:
                date_mapper[key] = 'None'
            else:
                date_mapper[key] = 'January' + ' ' + year[0]
        else:
            date_mapper[key] = value
    return date_mapper

    
def summarize_text(text):
    '''
    This function converts text into list of summary and saves it as a dataframe
    '''
    # Convert text to chunks
    text_list = get_chunks(text)
    #check if it violates content moderation guidelines by openai
    response = content_moderation(text_list)
    if response:
        return None,None
    
    no_of_chunks = len(text_list)
    
    # Get list of summary from chunks
    summary_list,token_list = get_list_of_summary(text_list)
    
    # Process summary list
    summary_list = process_summary(summary_list)
    
    #get the time when chatgpt was run
    todays_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    date_alignment_error = False
    
    #get summary dataframe from summary list
    summary_df = pd.DataFrame(data = summary_list,columns = ['Date','Event'])

    # Try the date ordering algorithm, if it doesnt work, skip the algorithm and go with default ordering
    try:
        #strip any space from front and back of the date
        summary_df['Date'] = summary_df['Date'].str.strip()
    
        #select 1 out of multiple events with same date (because most likely its repeated events)
        summary_df = summary_df.groupby('Date').first().reset_index()

        #get approximate month year from dates list
        date_map = get_approx_month_year(summary_df)

        #add timeline location to summary_df date
        summary_df['timeline'] = summary_df['Date'].map(date_map)
 
        #get month year and AD/BC from month year chatGPT output
        try:
            summary_df[['month', 'year', 'AD_BC']] = summary_df['timeline'].str.split(expand=True)
        except :
            #in case ad bc is still not available, add ad seperately in the end
            summary_df[['month', 'year']] = summary_df['timeline'].str.split(expand=True)
            summary_df['AD_BC'] = 'AD'
    
        # #if BC make year negative
        summary_df['year_loc'] = summary_df['year'].astype(int)*summary_df['AD_BC'].apply(lambda x : isBC(x))
    
        #order by year and month
        summary_df = summary_df.sort_values(['year_loc','month']).reset_index(drop = True)
    except:
        #flag if error in date ordering algorithm
        date_alignment_error = True

    summary_df['Order'] = list(range(1,summary_df.shape[0]+1))

    #gpt usage data stored for debugging in google sheets
    gpt_meta_data = []
    return summary_df,gpt_meta_data

 
