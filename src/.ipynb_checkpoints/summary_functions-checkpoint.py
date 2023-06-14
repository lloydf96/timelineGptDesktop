from langchain.text_splitter import CharacterTextSplitter
import tiktoken
### https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb

ENCODING_NAME = "gpt-3.5-turbo"
CHUNK_SIZE = 4000
CHUNK_OVERLAP = 1000

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
            {"role": "user", "content": f"For the text below, give a list of all events with dates? Begin" +\
             f" the bullet points with '{BULLET_SIGN}' and seperate date and event with ':' \n\n Text : {text}"}
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
    #split date:event into date,event
    summary_list = [event.split(':',1) for event in summary_list]

    #remove empty events
    summary_list = [event for event in summary_list if len(event[0])>0]

    #remove \n in event description
    summary_list = [[date,event.replace('\n','')] for [date,event] in summary_list]
    
    return summary_list


def summarize_text(text)
    '''
    This function converts text into list of summary
    '''
    # Convert text to chunks
    text_list = get_chunks(text)

    # Get list of summary from chunks
    summary_list = get_list_of_summary(text_list)

    # Process summary list
    summary_list = process_summary(summary_list)
    return summary_list


