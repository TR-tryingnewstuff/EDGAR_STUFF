#%%
"""
Maximum requests to sec EDGAR are 10/seconds
"""
from trafilatura import extract
import regex as re
import bs4
from config import DATAPATH, items_10k
import os
from tqdm import tqdm


def get_filing_sections(text_filing: str, sections=items_10k) -> dict:
    """
    Takes as input a filing text and returns 
    a dict with keys being the section name, and values the text of the section
    """

    no_space = re.sub('\s', '', text_filing)
    splits = re.split('(\s)', text_filing)

    # Locate each sections regex in <no_space>
    # We truncate the search to the left based 
    # on the previous item position
    prev_start = 0
    section_dict = {}
    for key in sections:


        item = re.search(sections[key], no_space[prev_start:], flags=re.IGNORECASE | re.DOTALL)

        if item:
            pos = item.span()[0]
            section_dict[key] = pos + prev_start
            prev_start = pos + prev_start


    # Convert the <no_space> position 
    # into the position with spaces included
    count_no_space = 0
    count = 0
    idx = 0

    for key in section_dict:

        while count < section_dict[key]:

            token = splits[idx]

            if not re.search('\s', token):
                count += len(token)

            count_no_space += len(token)

            idx += 1

        section_dict[key] = count_no_space

    
    sections_indexes = list(section_dict.values())

    # For each sections get the corresponding
    # portion of the text 
    for i, key in enumerate(section_dict):

        if i < len(sections_indexes) - 1:

            section_dict[key] = text_filing[ sections_indexes[i] : sections_indexes[i+1] ]

        else:
            section_dict[key] = text_filing[ sections_indexes[i] : ]

    return section_dict


def download_section(filepath, sections=items_10k):

        year = filepath.split('/')[-2]
        filename = filepath.split('/')[-1]

        try:
            text = open(filepath, 'r').read()

            sections = get_filing_sections(text, sections=sections)

            for section in sections:

                clean_text = re.sub('\n(\n|\s)+', '\n', str(sections[section]))

                with open(f"{DATAPATH}sections/{section}/{year}/{filename}", 'w+') as section_file:

                    section_file.write(clean_text)

        except Exception as e:
            print(e)


def get_filing_text_bs4(resp_content: str) -> str:

    # ? Dealing with different formats
    if re.search('xml', ''.join(resp_content.splitlines()[0:10])):
        soup = bs4.BeautifulSoup(resp_content, 'lxml-xml')

        # ? If XML, remove the first <div> that is not displayed 
        divs = soup.find_all('div')
        for div in divs:
            if re.search('display:\s*none', str(div.get('style')), flags=re.I):
                div.replace_with('')
                break

    # ? If html
    elif re.search('html', ''.join(resp_content.splitlines()[0:20])):
        soup = bs4.BeautifulSoup(resp_content, 'lxml')

    # ? Else
    else:
        soup = bs4.BeautifulSoup(resp_content, 'lxml')
        return soup.text


    # ? Removing tables
    tables = (t for t in soup.find_all('table'))
    for t in tables:
        t_text = t.text
        if len(re.sub('[a-zA-Z ]', '', t_text)) > len(re.sub(' ', '', t_text)) * 0.4:
            t.replace_with('\n\n')

    titles = (t for t in soup.find_all(['b', 'strong', 'h1', 'h2', 'h3', 'h4', 'h5', 'u']))
    for t in titles:

        t.replace_with(f"\n{t.text.upper()}\n")

    bold = (t for t in soup.find_all(['div', 'font', 'p', 'span']))

    for b in bold:
        if re.search('bold|underline', str(b.get('style'))):
            b.replace_with(f"\n{b.text.upper()}\n")

    # ? Get Text
    text = soup.get_text(' ')

    # ? Remove <table of contents>
    text = re.sub('\s*table of contents\s*', ' ', text, flags=re.IGNORECASE)    

    # ? Deal with spaces and non-ASCIIi
    text = re.sub('\xa0|&nbsp', ' ', text, flags=re.I)
    #text = re.sub('[^\x00-\x7F]', ' ', text)

    #sentences = re.split('(\n)', text)
    #text = ''.join([s for s in sentences if re.search('[a-zA-Z]', s)])    

    # ? Replace multi-endlines with unique endline
    text = re.sub('\s\s(\n|\s)+', '\n\n', text)

    return text


def get_filing_text_trafilatura(resp_content: str) -> str:

    text = extract(resp_content, include_tables=False)
    if text:
        if len(re.findall('gaap', text.splitlines()[0])):
            text = '\n'.join(text.splitlines()[1:])

    return text


def get_filing_text(resp_content: str) -> str:
        
        # Try parsing with trafilatura
        text = get_filing_text_trafilatura(resp_content)

        # If trafilatura doesn't work, fallback to bs4
        if not text:
            text = get_filing_text(resp_content)

        return text


def clean_and_download_filing(f, form):

    if not os.path.isdir(f'{DATAPATH}/{form}'):
        os.mkdir(f'{DATAPATH}/{form}')


    chunks = f.split('/')[-1].split('_')
    year = chunks[2].split('-')[0]

    folder_path = f'{DATAPATH}/{form}/{year}/'

    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)

    new_filename = f.split('/')[-1].replace('.html', '.txt')


    text = get_filing_text_trafilatura(open(f, 'r', errors="replace").read())

    if text:
        with open(f'{folder_path}{new_filename}', 'w+') as f:
            f.write(text)


# %%