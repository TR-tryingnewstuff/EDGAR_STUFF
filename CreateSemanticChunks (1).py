#%%
import regex as re
import glob 
from joblib import Parallel, delayed
import pandas as pd
from sentence_transformers import SentenceTransformer
import nltk
from semantic_text_splitter import TextSplitter

t_splitter = TextSplitter((200, 1000))


def sem_text_splitter(text):
    text = t_splitter.chunks(text)
    text = [re.sub('[^a-zA-Z,\:;\.\?\!\-\s&\']', ' ', t) for t in text]
    text = [re.sub('\n', ' ', t) for t in text]
    text = [re.sub(' +', ' ', t).strip() for t in text]

    return text

SSD_PATH = '/media/fast-pc-2023/08b6088c-6c22-4f96-bc7b-70f9d70f21a5/EDGAR_DATA/Risk_Sentences2/'


def create_paragraph_files_per_year(chunk_text_func, risks_only=False):

    risk_related_kw = ['risks?', 'could', 'can', 'material', 'cannot', 'subject to', 'affect', 'potential', 'depends?', 'expos(ed|es|ures?)',  'fluctuations?', 'uncertain(ty|ties|)', 'likely to', 'influences?', 'susceptible', 'adverse(ly)?', 'negative(ly)?', 'impacts?', 'effects?', 'harm', 'ability to', 'unable to', 'forced to', 'obliged to']# 'may',
    risk_pattern = '( |,|\.|;)|( |,|\.|;)'.join(risk_related_kw)
    # First we split all 1A Items into smaller chunks
    for year in range(2021, 2025):
        files = glob.glob(f'/media/fast-pc-2023/08b6088c-6c22-4f96-bc7b-70f9d70f21a5/EDGAR_DATA/10-K_sections/1A/{year}/*')

        chunks_chunks = Parallel(16, backend='multiprocessing')(delayed(chunk_text_func)(open(f).read()) for f in files)

        with open(f'{SSD_PATH}{year}.txt', 'w+') as text_file:
            
            for chunks in chunks_chunks:
                for c in chunks:
                    if len(c.split()) > 5:
                        if risks_only:
                            if re.search(risk_pattern, c, flags=re.I):
                                text_file.write(c + '\n')

                        else:
                            text_file.write(c + '\n')

    
    # Then we remove duplicate chunks
    for year in range(2021, 2025):

        filename = f'{SSD_PATH}{year}.txt'
        chunks = open(filename).read().splitlines()
        chunks = list(set(chunks))

        with open(filename, 'w+') as text_file:
            text_file.write('\n'.join(chunks))


def get_embedding_df_per_year():
    model = SentenceTransformer("all-MiniLM-L6-V2", device='cpu')
    chunks = set()
    for year in range(2021, 2025):
        filename = f'{SSD_PATH}/{year}.txt'
        chunks.update(open(filename).read().splitlines())
    
    chunks = list(chunks)
    print(len(chunks))
    for idx in range(0, len(chunks), 500000):    
        embeddings = model.encode(chunks[idx:idx+500000], show_progress_bar=True)

        df = pd.DataFrame([chunks[idx:idx+500000], embeddings]).T
        df.columns = ['content', 'embedding']

        df.to_parquet(f'Item1A_semsplit_{idx}.pq', index=False)

text = open("/media/fast-pc-2023/08b6088c-6c22-4f96-bc7b-70f9d70f21a5/EDGAR_DATA/10-K_sections/1A/2024/ALRN_10-K_2024-04-15.txt").read()

sem_text_splitter(text)
