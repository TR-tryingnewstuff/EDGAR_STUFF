#%%
import pandas as pd
import requests
from config import HEADERS, CIK_DF
from tqdm import tqdm

def download_cik_tickers():

    url = 'https://www.sec.gov/files/company_tickers.json'
    response = requests.get(url, headers=HEADERS)

    cik_df = pd.DataFrame(response.json()).T
    cik_df['cik'] = cik_df['cik_str']
    cik_df['cik_str'] = cik_df['cik_str'].apply(lambda x : ('0'*10)[:10 - len(str(x))] + str(x))
    cik_df = cik_df.drop_duplicates()

    cik_df.to_parquet(CIK_DF, index=False)

    print('************ SUCCESSFUL DOWNLOAD **************')

    return cik_df


def get_cik_from_ticker(ticker: str):
    '''Returns cik of the given ticker'''

    cik_df = pd.read_parquet(CIK_DF).set_index('ticker')
    cik = cik_df.loc[ticker.upper()]['cik_str']

    return cik


def get_ticker_from_cik(cik: str):
    '''Returns cik of the given ticker'''

    cik_df = pd.read_parquet(CIK_DF).set_index('cik_str')
    ticker = cik_df.loc[cik]['ticker']

    if not isinstance(ticker, str):
        ticker = ticker.iloc[0]

    return ticker


def get_filings_json(cik: str|None =None) -> dict:

    url = f'https://data.sec.gov/submissions/CIK{cik}.json'
    response = requests.get(url, headers=HEADERS)

    return response.json()


def get_company_financials(cik: str|None = None) -> dict:


    url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json'
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 404:
        return 

    statements = response.json()['facts'].get('us-gaap')

    if not statements:
        return

    financials = {}
    for info in statements:

        financials[info] = {}
        
        try:
            lines = statements[info]['units']['USD']
            for l in lines:
                financials[info][l.get('filed')] = l.get('val')

        except KeyError as e:
            pass

    df = pd.DataFrame(financials).sort_index()
    df['cik_str'] = [cik] * len(df)

    # ! Filter out columns that have above 20% of NaN values
    df = df.dropna(thresh=int(len(df) * 0.2), axis=1)

    return df


def get_company_sec_info(cik=None, ticker=''):

        results = get_filings_json(cik=cik)

        results = {
            'name': results.get('name'),
            'cik' : results.get('cik'),
            'entityType': results.get('entityType'),
            'sic': results.get('sic'),
            'sicDescription': results.get('sicDescription'),
            'tickers': results.get('tickers'),
            'category': results.get('category'),
            'formerNames': results.get('formerNames'),
            "stateOfIncorporation": results.get('stateOfIncorporationDescription'),
            "stateOfBusinessAddress": results['addresses']['business'].get('stateOrCountryDescription'),
        }   

        return results


def download_company_infos():

    ciks = pd.read_parquet(CIK_DF)['cik_str'].unique().tolist()

    company_infos = []
    for cik in tqdm(ciks):
        info = get_company_sec_info(cik)
        company_infos.append(info)

    df = pd.DataFrame(company_infos)
    df.to_parquet('company_infos.csv', index=False)


def get_company_filings_info(sec_submission_json: dict):
    """
    The function takes as inputs the results from the <get_filings_json> function
    That is the json found at the url : https://data.sec.gov/submissions/CIK{cik}.json'

    The function returns a DataFrame of the resulting filings information for the 
    given company
    """

    jsons = []
    jsons.append(sec_submission_json['filings']['recent'])

    # ? When there are too many filings, they are split accross multiple URLs
    if files := sec_submission_json['filings'].get('files', None):
        
        for f in files:

            end_url = f['name']
            url = f'https://data.sec.gov/submissions/{end_url}'
            
            json = requests.get(url, headers=HEADERS).json()
            jsons.append(json)       
    

    df = pd.concat([pd.DataFrame(f) for f in jsons])

    return df


def get_filings_df(cik:str =None, form: str =''):
    """
    Returns a df with the following columns :
    
    accessionNumber -> file specific number \n
    filingDate \n
    reportDate \n
    form -> filing form (10-K, 10-Q, 8-K...) \n
    primaryDocument -> end of url \n
    ticker \n
    cik_str \n
    cik \n
    url \n
    """

    def get_url(line):
        """Utility function to get the URL storing the report"""

        cik = line['cik']
        accession_number = line['accessionNumber']
        accession_number_strip = accession_number.replace('-', '')

        # ? the txt version of Old documents can be accessed with the pattern {accession_number}.txt
        document = line['primaryDocument'] if line['primaryDocument'] else accession_number + '.txt'

        url = f'https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number_strip}/{document}'

        return url

    ticker = get_ticker_from_cik(cik)
    filings_json = get_filings_json(cik=cik)

    df = get_company_filings_info(filings_json)

    df['ticker'] = [ticker] * len(df)
    df['cik_str'] = [cik] * len(df)
    df['cik'] = [cik.lstrip('0')] * len(df)
    
    if form:
        df = df.loc[df['form'].str.startswith(form)]

    df['url'] = df.apply(get_url, axis=1)
    
    return df


# %%
