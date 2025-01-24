#%%
from utils_sec_infos import *
from utils_filings import *
from config import DATAPATH, HEADERS, items_10k, items_10q


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


# FIRST WE DOWNLOAD A DF OF ALL PUBLICLY TRADED FIRMS FROM THE SEC
download_cik_tickers()

# HERE ARE TWO UTIL FUNCTIONS TO TRANSFORM A CIK to a TICKER and VICE VERSA
print(get_ticker_from_cik("0000320193"))
print(get_cik_from_ticker("AAPL"))


# WITH THIS YOU CAN DOWNLOAD A FILLING FROM THE SEC
download_company_filings("0000320193", form='10-Q', limit=100) # FILLING FROM APPLE

# FINALLY THIS FUNCTION SPLITS THE TEXT INTO CHUNKS
download_section("/Users/main/Desktop/EDGAR/EDGAR_DATA/10-Q/TEXT/2024/AAPL_10-Q_2024-08-02.txt", sections=items_10q)
