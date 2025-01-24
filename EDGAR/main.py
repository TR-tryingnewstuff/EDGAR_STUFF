#%%
from utils_sec_infos import *
from utils_filings import *
from config import DATAPATH, HEADERS, items_10k, items_10q


def fetch_feed_items(response: requests.Response) -> list[dict]:

    soup_items = bs4.BeautifulSoup(response.content, 'lxml-xml').find_all('item')
    
    items = []
    for soup_item in soup_items:
        
        item = {}
        for info in soup_item:
            
            if info.text:

                if not item.get(info.name):
                    item[info.name] = info.text

                elif isinstance(item.get(info.name), list):
                    item[info.name].append(info.text)

                else:
                    item[info.name] = [item[info.name]]
                    item[info.name].append(info.text)
                
        item.pop(None)
        items.append(item)

    return items


def download_company_filings(cik: str, form: str ='10-K', download_text=True, download_html=False, limit=1):

    try: ticker = get_ticker_from_cik(cik)
    
    except: 
        infos = get_company_sec_info(cik)
        
        if not infos['tickers']:
            print(f"No ticker found for {infos.get('name')} with CIK : {cik}")
            return False
        ticker = infos['tickers'][0]

    df = get_filings_df(cik, form=form).iloc[:limit]

    for url, date, form in zip(df['url'], df['filingDate'], df['form']):
        
        form = re.sub('/', '',form)
        folder_path = f'{DATAPATH}{form}'
        filename = f"{ticker}_{form}_{date}"

        html_path = f'{folder_path}/HTML/{date[:4]}/{filename}.html'
        text_path = f'{folder_path}/TEXT/{date[:4]}/{filename}.txt'        

        
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            return False
        
        content = response.content

        if download_html & (not os.path.isfile(html_path)):
            with open(html_path, 'wb+') as f:
                f.write(content)


        if download_text:# & (not os.path.isfile(text_path)):
            with open(text_path, 'w+') as f:
                
                text = get_filing_text(content)
                f.write(text)
                
                if re.search('10-K', form):
                    download_section(text_path)

    return True


def update_filings():

    url = 'https://www.sec.gov/Archives/edgar/usgaap.rss.xml'
    items = fetch_feed_items(requests.get(url, headers=HEADERS))

    for item in items:
        if re.search('10-K', item['description']):

            form = item['description']
            cik = item['xbrlFiling'].split('\n')[4]
        
            download_company_filings(cik, form, True, True, 1)


def get_company_embedding(ticker, model, max_seq=230, keep_n_first=3):
    import glob
    files = glob.glob(f'{DATAPATH}10-K_sections/1/202[0-9]/*')
    files = [f for f in files if re.search(ticker.upper(), f)]
    files.sort()
    file_ = files[-1]
    
    ticker = file_.split('/')[-1].split('_')[0]

    text = open(file_).read()[:100000]
    text = re.sub('[0-9]', '', text)
    tokens = text.split()
    chunks = [' '.join(tokens[i*max_seq:(i+1)*max_seq]) for i in range(len(tokens)//230)]

    embeddings = model.encode(chunks[:keep_n_first]).mean(axis=0)

    return embeddings


# FIRST WE DOWNLOAD A DF OF ALL PUBLICLY TRADED FIRMS FROM THE SEC
download_cik_tickers()

# HERE ARE TWO UTIL FUNCTIONS TO TRANSFORM A CIK to a TICKER and VICE VERSA
print(get_ticker_from_cik("0000320193"))
print(get_cik_from_ticker("AAPL"))


# WITH THIS YOU CAN DOWNLOAD A FILLING FROM THE SEC
download_company_filings("0000320193", form='10-Q', limit=100) # FILLING FROM APPLE

# FINALLY THIS FUNCTION SPLITS THE TEXT INTO CHUNKS
download_section("/Users/main/Desktop/EDGAR/EDGAR_DATA/10-Q/TEXT/2024/AAPL_10-Q_2024-08-02.txt", sections=items_10q)
