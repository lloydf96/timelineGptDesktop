# -*- coding: utf-8 -*-
"""data_extract.py

Created by Praveen Kumar Murugaiah, parveen00@gmail.com
Automatically generated by Colaboratory.

"""

# Import all the necessary packages

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

def get_wiki_link(search_term):
  url = f'https://en.wikipedia.org/w/index.php?search={search_term}&title=Special:Search&profile=advanced&fulltext=1&ns0=1'
  page = requests.get(url)
  soup = BeautifulSoup(page.content, "html.parser")
  
  links = []
  main_url = 'https://en.wikipedia.org/'
  for link in soup.findAll('a'):
    links.append(link['href'])
    
  if 'redlink' in links[30]:
    if 'offset' in str(links[32]):
      for link in links[32:]:
        if '/wiki/' in link:
          return link
    else:
      return 'NONE'
  elif '/wiki/' in links[30]:
    return links[30]
    
  if 'Special:Search' in links[30]:
    for link in links[31:]:
      if '/wiki/' in link and 'Article_wizard' not in link:
        return link


# Get the content from Wikipedia
def get_wikipedia_text(link):
  page = requests.get(link)
  soup = BeautifulSoup(page.content, "html.parser")
  final_texts = []
  for p in soup.findAll('p'):
    text = p.text.strip()
    text = re.sub(r'[[0-9]+]', '', text)
    final_texts.append(text)
  final_text = ' '.join(final_texts).strip().replace("\'s","'s")
  return final_text

# Since our chatGPT api can work with max 90,000 tokens per minute, we will cap the number of tokens in our wikipedia text

# # Save the text to file
# text_file = open("output.txt", "w")
# text_file.write(final_text)
# text_file.close()

