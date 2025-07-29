DEFAULT_VNDIRECT_DOMAIN = 'vndirect.com.vn'
DEFAULT_VNDIRECT_STOCK_INDEX_BASE_URL = 'https://api-finfo.vndirect.com.vn/v4/stock_prices'
DEFAULT_VNDIRECT_FUNDAMENTAL_INDEX_BASE_URL = 'https://api-finfo.vndirect.com.vn/v4/ratios/latest'
DEFAULT_VNDIRECT_FINANCIAL_MODELS_BASE_URL = 'https://api-finfo.vndirect.com.vn/v4/financial_models'
DEFAULT_VNDIRECT_FINANCIAL_STATEMENTS_BASE_URL = 'https://api-finfo.vndirect.com.vn/v4/financial_statements'
DEFAULT_VNDIRECT_HEADERS = {
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'Origin': 'https://dstock.vndirect.com.vn',
    'Referer': 'https://dstock.vndirect.com.vn/'
}

DEFAULT_24HMONEY_DOMAIN = '24hmoney.vn'
DEFAULT_24HMONEY_BASE_URL = 'https://api-finance-t19.24hmoney.vn/v1/ios/company/az'
DEFAULT_24HMONEY_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
    'Origin': 'https://24hmoney.vn',
    'Referer': 'https://24hmoney.vn/',
    'Sec-Ch-Ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
}

DEFAULT_TIMEOUT = 300.0
DEFAULT_TIMEOUT_CONNECT = 150.0