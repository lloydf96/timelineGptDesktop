import requests
from langchain.text_splitter import CharacterTextSplitter
import tiktoken
import pandas as pd
import openai
import ast
import re
import os
import streamlit as st
### https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb

ENCODING_NAME = "gpt-3.5-turbo"
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 500
BULLET_SIGN = '->'
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
    
    text_splitter = CharacterTextSplitter(        
        separator = ". ",
        chunk_size = chunk_size,
        chunk_overlap  = chunk_overlap,
        length_function = num_tokens_from_string,
    )

    #add full stop in end
    text_list = [x + "." for x in text_splitter.split_text(text)]
    return text_list


def get_summary(text):
    '''
    Get summary from chatGPT from a text input
    '''
    #replace Bullet sign with no space
    text = text.replace(BULLET_SIGN,"")
    
    result = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are an extractive summarizer"},
            {"role": "user", "content": f"For the text below, please extract all events along with their dates in the form of a list. Begin" +\
             f" the bullet points with '{BULLET_SIGN}' and separate date and event with ':'. Each event list should begin with the date followed by the event description \n\n Text : {text}"}
        ],temperature = 0)

    response = result.choices[0].message.content
    if "\n\n" in response:
        response = response.split("\n\n")[1]

    return response


def get_list_of_summary(text_list):
    '''
    Get list of summaries from list of text chunks
    '''
    #get list of summaries
    summary_list = [get_summary(text) for text in text_list]

    #split each summary into list
    summary_list = [summary.split(BULLET_SIGN) for summary in summary_list]
    
    #convert list of list into a single list
    summary_list = [event for sublist in summary_list for event in sublist]

    return summary_list


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
    try:
        if 'BC' in x:
            return -1
        else:
            return 0
    except:
        return 0

def validate_url(url_link):
    '''
    This function checks if the input url is a valid url or not. If valid, returns the url. If invalid, it returns a message displaying that link is invalid
    '''
    
    try:
        response = requests.get(url_link)
    except:
        return 'Not a Valid URL Link'

    if str(response) == '<Response [200]>':
        return url_link

def get_approx_month_year(df):
    list_of_dates = df['Date'].tolist()
    result = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a function that gives a single month year approximation for a list of phrases"},
            {"role": "user", "content":  f'''for the list of phrase give a list of month year approximation {list_of_dates}. Format the list as follows: If spans across centuries, give a single representative month and year that lies in the period. Give the output in the format <input phrase>-><output month> <output year along with BC or AD time system>. If <output year> > 10000, give 10000. Give each element of the list one below the other.'''}
        ],temperature = 0)

    response = result.choices[0].message.content
    if "\n\n" in response:
        response = response.split("\n\n")[1]

    # print(response)
    dates = response.split('\n')
    # print(dates)
    date_mapper = dict()
    for date in dates:
        # print(date)
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
    
def isBC(x):
    try:
        if 'BC' in x:
            return -1
        else:
            return 1
    except:
        return 1
        
def summarize_text(text):
    '''
    This function converts text into list of summary and saves it as a dataframe
    '''
    # Convert text to chunks
    text_list = get_chunks(text)

    # Get list of summary from chunks
    summary_list = get_list_of_summary(text_list)

    # Process summary list
    summary_list = process_summary(summary_list)

    #get summary dataframe from summary list
    summary_df = pd.DataFrame(data = summary_list,columns = ['Date','Event'])

    try:
        #strip any space from front and back of the date
        summary_df['Date'] = summary_df['Date'].str.strip()
    
        #select 1 out of multiple events with same date (because most likely its repeated events)
        summary_df = summary_df.groupby('Date').first().reset_index()
        
        #get approximate month year from dates list
        date_map = get_approx_month_year(summary_df)
        
        # print(date_map)
        
        
        #add timeline location to summary_df date
        summary_df['timeline'] = summary_df['Date'].map(date_map)
    
        #return summary_df,date_map
        #get month year and AD/BC from month year chatGPT output
        summary_df[['month', 'year', 'AD_BC']] = summary_df['timeline'].str.split(expand=True)
    
        # #if BC make year negative
        summary_df['year_loc'] = summary_df['year'].astype(int)*summary_df['AD_BC'].apply(lambda x : isBC(x))
    
        #order by year and month
        summary_df = summary_df.sort_values(['year_loc','month']).reset_index(drop = True)

        # a = 1/0
        
    except:
        summary_df.to_pickle(os.path.join(os.getcwd(),'data','log_summary_df.pkl'))
    
    return summary_df

    
# def get_approx_month_year(df):
#     list_of_dates = df['Date'].tolist()
#     result = openai.ChatCompletion.create(
#       model="gpt-3.5-turbo",
#       messages=[
#             {"role": "system", "content": "You are a function that gives a single month year approximation for a list of phrases"},
#             {"role": "user", "content":  f"for the list of phrase give a list of month year approximation {list_of_dates}. Format the list as follows: If spans across centuries, give a single representative month and year that lies in the period. Give the output in the format [ <input phrase>:  <output month> <output year along with BC or AD time system>]. If <output year> > 10000, give None"}
#         ],temperature = 0)

#     response = result.choices[0].message.content
#     if "\n\n" in response:
#         response = response.split("\n\n")[1]
        
#     dates = response.split('\n')
#     date_mapper = dict()
#     for date in dates:
#         key, value = re.sub(r'[^A-Za-z0-9\,\': ]+', '', date).strip().split(': ')
#         key =  re.sub(r'[\']+', '', key)
#         value =  re.sub(r'[\,\']+', '', value)
        
#         # Check chatGPI returns None when there is year in the input data
#         # If yes, get the year and add 'January' as default month
#         # If No, then skip this process
        
#         if value == 'None':
#             year = re.search(f'[0-9].*', value)
#             if year == None:
#                 date_mapper[key] = 'None'
#             else:
#                 date_mapper[key] = 'January' + ' ' + year[0]
#         else:
#             date_mapper[key] = value
#     return date_mapper


# def summarize_text(text):
#     '''
#     This function converts text into list of summary and saves it as a dataframe
#     '''
#     # Convert text to chunks
#     text_list = get_chunks(text)

#     # Get list of summary from chunks
#     summary_list = get_list_of_summary(text_list)

#     # Process summary list
#     summary_list = process_summary(summary_list)

#     #get summary dataframe from summary list
#     summary_df = pd.DataFrame(data = summary_list,columns = ['Date','Event'])

#     #strip any space from front and back of the date
#     summary_df['Date'] = summary_df['Date'].str.strip()

#     #select 1 out of multiple events with same date (because most likely its repeated events)
#     summary_df = summary_df.groupby('Date').first().reset_index()
    
#     #get approximate month year from dates list
#     date_map = get_approx_month_year(summary_df)
    
#     print(date_map)
#     print(summary_df)
    
#     #add timeline location to summary_df date
#     summary_df['timeline'] = summary_df['Date'].map(date_map)

#     #get month year and AD/BC from month year chatGPT output
#     summary_df[['month', 'year', 'AD_BC']] = summary_df['timeline'].str.split(expand=True)

#     #if BC make year negative
#     summary_df['year'] = summary_df['year']*(summary_df['AD_BC'].apply(lambda x : isBC(x)))

#     #order by year and month
#     summary_df = summary_df.sort_values(['year','month'])
    
#     return summary_df


def summarize_text_old(text):
    '''
    This function converts text into list of summary and saves it as a dataframe
    '''
    # Convert text to chunks
    text_list = get_chunks(text)

    # Get list of summary from chunks
    summary_list = get_list_of_summary(text_list)

    # Process summary list
    summary_list = process_summary(summary_list)
    summary_df = pd.DataFrame(data = summary_list,columns = ['Date','Event'])
    
    return summary_df


