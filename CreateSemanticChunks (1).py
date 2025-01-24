#%%
import regex as re
import glob 
import pandas as pd
import nltk
from semantic_text_splitter import TextSplitter

t_splitter = TextSplitter((200, 1000))


def sem_text_splitter(text):
    text = t_splitter.chunks(text)
    text = [re.sub('[^a-zA-Z,\:;\.\?\!\-\s&\']', ' ', t) for t in text]
    text = [re.sub('\n', ' ', t) for t in text]
    text = [re.sub(' +', ' ', t).strip() for t in text]

    return text


text = open("/media/fast-pc-2023/08b6088c-6c22-4f96-bc7b-70f9d70f21a5/EDGAR_DATA/10-K_sections/1A/2024/ALRN_10-K_2024-04-15.txt").read()

sem_text_splitter(text)
