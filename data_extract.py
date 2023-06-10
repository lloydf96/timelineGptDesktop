# -*- coding: utf-8 -*-
"""extract

Created by Praveen Kumar Murugaiah, parveen00@gmail.com
Automatically generated by Colaboratory.

"""

# Import all the necessary packages
from googlesearch import search
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import warnings
warnings.filterwarnings('ignore')

'''
Google search link function takes in the search_term we need to search for and 
  then returns the first wikipedia link from the google search
'''
def google_search_link(search_term):
  query = "wikipedia " + search_term

  for j in search(query, tld="co.in", num=2, stop=10, pause=2):
	  return j

wikipedia_link = google_search_link('nvidia')

# Get the content from Wikipedia
def get_wikipedia_text(wikipedia_link):
  page = requests.get(wikipedia_link)
  soup = BeautifulSoup(page.content, "html.parser")
  final_texts = []
  for p in soup.findAll('p'):
    text = p.text.strip()
    text = re.sub(r'[[0-9]+]', '', text)
    final_texts.append(text)
  final_text = ' '.join(final_texts).strip().replace("\'s","'s")

  # Since our chatGPT api can work with max 90,000 tokens per minute, we will cap the number of tokens in our wikipedia text
  all_tokens = final_text.split()
  no_of_tokens = len(all_tokens)

  if no_of_tokens >= 90000:
    return ' '.join(all_tokens[:90000])
  return final_text

final_text = get_wikipedia_text(wikipedia_link)

# Save the text to file
text_file = open("output.txt", "w")
text_file.write(final_text)
text_file.close()

