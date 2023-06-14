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

def get_chunks(text):
    '''
    Split a single document into multiple chunks of size less than CHUNK_SIZE and overlap
    of CHUNK_OVERLAP.
    The chunking is done with a "." seperator
    '''
    
    assert type(text) == str, "text file is not of type string recheck"
    
    text_splitter = CharacterTextSplitter(        
        separator = ".",
        chunk_size = CHUNK_SIZE,
        chunk_overlap  = CHUNK_OVERLAP,
        length_function = num_tokens_from_string,
    )
    
    text_list = text_splitter.split_text(text)
    return text_list
