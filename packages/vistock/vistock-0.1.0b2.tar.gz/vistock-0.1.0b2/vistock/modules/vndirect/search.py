from vistock.core.constants import (
    DEFAULT_VNDIRECT_STOCK_INDEX_BASE_URL,
    DEFAULT_VNDIRECT_FUNDAMENTAL_INDEX_BASE_URL, 
    DEFAULT_VNDIRECT_DOMAIN, 
    DEFAULT_TIMEOUT
)
from vistock.core.models import (
    StandardVnDirectStockIndex,
    AdvancedVnDirectStockIndex,
    StandardVnDirectStockIndexSearchResults,
    AdvancedVnDirectStockIndexSearchResults,
    StandardVnDirectFundamentalIndexSearchResults
)
from vistock.modules.vndirect.scrapers import (
    VistockVnDirectStockIndexScraper,
    VistockVnDirectFundamentalIndexScraper
)
from vistock.modules.vndirect.parsers import (
    VistockVnDirectStockIndexParser,
    VistockVnDirectFundamentalIndexParser
)
from vistock.core.utils import VistockValidator
from typing import List, Dict, Union, Literal, Any, overload
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

class VistockVnDirectStockIndexSearch:
    def __init__(self, timeout: float = DEFAULT_TIMEOUT, **kwargs: Any) -> None:
        if timeout <= 0:
            raise ValueError(
                'Invalid configuration: "timeout" must be a strictly positive integer value representing the maximum allowable wait time for the operation.'
            )
        self._timeout = timeout

        if 'semaphore_limit' in kwargs and (not isinstance(kwargs['semaphore_limit'], int) or kwargs['semaphore_limit'] <= 0):
            raise ValueError(
                'Invalid configuration: "semaphore_limit" must be a positive integer, indicating the maximum number of concurrent asynchronous operations permitted.'
            )

        self._semaphore_limit = kwargs.get('semaphore_limit', 5)
        self._base_url = DEFAULT_VNDIRECT_STOCK_INDEX_BASE_URL
        self._domain = DEFAULT_VNDIRECT_DOMAIN
        self._scraper = VistockVnDirectStockIndexScraper()
        self._parser = VistockVnDirectStockIndexParser()
        self._semaphore = asyncio.Semaphore(self._semaphore_limit)

    @property
    def timeout(self) -> float:
        return self._timeout
    
    @timeout.setter
    def timeout(self, value: int) -> None:
        if value <= 0:
            raise ValueError(
                'Invalid value: "timeout" must be a positive integer greater than zero.'
            )
        self._timeout = value

    @overload
    def search(
        self,
        code: str,
        *,
        start_date: str,
        end_date: str,
        resolution: Literal['day', 'week', 'month', 'year']
    ) -> Union[StandardVnDirectStockIndexSearchResults, AdvancedVnDirectStockIndexSearchResults]:
        ...

    @overload
    def search(
        self,
        code: str,
        *,
        start_date: str,
        end_date: str,
        resolution: Literal['day', 'week', 'month', 'year'],
        advanced: bool
    ) -> Union[StandardVnDirectStockIndexSearchResults, AdvancedVnDirectStockIndexSearchResults]:
        ...

    @overload
    def search(
        self,
        code: str,
        *,
        start_date: str,
        end_date: str,
        resolution: Literal['day', 'week', 'month', 'year'],
        advanced: bool,
        ascending: bool
    ) -> Union[StandardVnDirectStockIndexSearchResults, AdvancedVnDirectStockIndexSearchResults]:
        ...

    def search(
        self,
        code: str,
        *,
        start_date: str = '2012-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        resolution: Literal['day', 'week', 'month', 'year'] = 'day',
        advanced: bool = True,
        ascending: bool = False
    ) -> Union[StandardVnDirectStockIndexSearchResults, AdvancedVnDirectStockIndexSearchResults]:
        try:
            if not VistockValidator.validate_code(code):
                raise ValueError(
                    'Invalid code: "code" must be a non-empty alphanumeric string with exactly 3 characters representing the stock code. Please ensure that the code is specified correctly.'
                )

            if not VistockValidator.validate_resolution(resolution):
                raise ValueError(
                    'Invalid resolution: "resolution" must be one of the following values: "day", "week", "month", or "year". Please ensure that the resolution is specified correctly.'
                )

            initial_url = f"{self._base_url}{self._parser.parse_url_path(code=code, start_date=start_date, end_date=end_date)}"
            total_elements = self._scraper.fetch(url=initial_url).get('totalElements', 0)

            url = f"{self._base_url}{self._parser.parse_url_path(code=code, start_date=start_date, end_date=end_date, limit=total_elements)}"
            data: List[Dict[str, Any]] = self._scraper.fetch(url=url).get('data', [])
            
            if not data:
                raise ValueError(
                    'No data found for the given parameters. Please check the code, start date, and end date to ensure they are correct and that data exists for the specified range.'
                )
            
            if not VistockValidator.validate_stock_index_json_data(data):
                raise ValueError(
                    'Invalid data format: The fetched data does not conform to the expected JSON structure. Please ensure that the API response is valid and contains the necessary fields.'
                )
            
            data.sort(key=lambda x: x.get("date", ""), reverse=not ascending)

            if advanced:
                return AdvancedVnDirectStockIndexSearchResults(
                    results=[AdvancedVnDirectStockIndex(**item) for item in data],
                    total_results=len(data)
                )

            return StandardVnDirectStockIndexSearchResults(
                results=[
                    StandardVnDirectStockIndex(
                        code=item['code'],
                        date=item['date'],
                        time=item['time'],
                        tfloor=item.get('floor', ''),
                        type=item['type'],
                        mopen=item['adOpen'],
                        mhigh=item['adHigh'],
                        mlow=item['adLow'],
                        mclose=item['adClose'],
                        maverage=item['adAverage'],
                        nmvolume=int(item['nmVolume'])
                    ) for item in data
                    if all(k in item for k in ['code', 'date', 'time', 'floor', 'type', 'adOpen', 'adHigh', 'adLow', 'adClose', 'adAverage', 'nmVolume'])
                ],
                total_results=len(data)
            ) 

        except Exception:
            logger.error("An unexpected error occurred during the search operation.", exc_info=True)
            raise

    @overload
    async def async_search(
        self,
        code: str,
        *,
        start_date: str,
        end_date: str,
        resolution: Literal['day', 'week', 'month', 'year']
    ) -> Union[StandardVnDirectStockIndexSearchResults, AdvancedVnDirectStockIndexSearchResults]:
        ...

    @overload
    async def async_search(
        self,
        code: str,
        *,
        start_date: str,
        end_date: str,
        resolution: Literal['day', 'week', 'month', 'year'],
        advanced: bool
    ) -> Union[StandardVnDirectStockIndexSearchResults, AdvancedVnDirectStockIndexSearchResults]:
        ...

    @overload 
    async def async_search(
        self,
        code: str,
        *,
        start_date: str,
        end_date: str,
        resolution: Literal['day', 'week', 'month', 'year'],
        advanced: bool,
        ascending: bool
    ) -> Union[StandardVnDirectStockIndexSearchResults, AdvancedVnDirectStockIndexSearchResults]:
        ...

    async def async_search(
        self,
        code: str,
        *,
        start_date: str = '2012-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        resolution: Literal['day', 'week', 'month', 'year'] = 'day',
        advanced: bool = True,
        ascending: bool = False
    ) -> Union[StandardVnDirectStockIndexSearchResults, AdvancedVnDirectStockIndexSearchResults]:
        try:
            if not VistockValidator.validate_code(code):
                raise ValueError(
                    'Invalid code: "code" must be a non-empty alphanumeric string with exactly 3 characters representing the stock code. Please ensure that the code is specified correctly.'
                )

            if not VistockValidator.validate_resolution(resolution):
                raise ValueError(
                    'Invalid resolution: "resolution" must be one of the following values: "day", "week", "month", or "year". Please ensure that the resolution is specified correctly.'
                )

            initial_url = f"{self._base_url}{self._parser.parse_url_path(code=code, start_date=start_date, end_date=end_date)}"
            initial_response = await self._scraper.async_fetch(url=initial_url)
            total_elements = initial_response.get('totalElements', 0)

            url = f"{self._base_url}{self._parser.parse_url_path(code=code, start_date=start_date, end_date=end_date, limit=total_elements)}"
            response = await self._scraper.async_fetch(url=url) 
            data: List[Dict[str, Any]] = response.get('data', [])

            if not data:
                raise ValueError(
                    'No data found for the given parameters. Please check the code, start date, and end date to ensure they are correct and that data exists for the specified range.'
                )

            if not VistockValidator.validate_stock_index_json_data(data):
                raise ValueError(
                    'Invalid data format: The fetched data does not conform to the expected JSON structure. Please ensure that the API response is valid and contains the necessary fields.'
                )

            data.sort(key=lambda x: x.get("date", ""), reverse=not ascending)

            if advanced:
                return AdvancedVnDirectStockIndexSearchResults(
                    results=[AdvancedVnDirectStockIndex(**item) for item in data],
                    total_results=len(data)
                )

            return StandardVnDirectStockIndexSearchResults(
                results=[
                    StandardVnDirectStockIndex(
                        code=item['code'],
                        date=item['date'],
                        time=item['time'],
                        tfloor=item.get('floor', ''),
                        type=item['type'],
                        mopen=item['adOpen'],
                        mhigh=item['adHigh'],
                        mlow=item['adLow'],
                        mclose=item['adClose'],
                        maverage=item['adAverage'],
                        nmvolume=int(item['nmVolume'])
                    ) for item in data
                    if all(k in item for k in ['code', 'date', 'time', 'floor', 'type', 'adOpen', 'adHigh', 'adLow', 'adClose', 'adAverage', 'nmVolume'])
                ],
                total_results=len(data)
            )

        except Exception:
            logger.error("An unexpected error occurred during the search operation.", exc_info=True)
            raise

class VistockVnDirectFundamentalSearch:
    def __init__(self, timeout: float = DEFAULT_TIMEOUT, **kwargs: Any) -> None:
        if timeout <= 0:
            raise ValueError(
                'Invalid configuration: "timeout" must be a strictly positive integer value representing the maximum allowable wait time for the operation.'
            )
        self._timeout = timeout

        if 'semaphore_limit' in kwargs and (not isinstance(kwargs['semaphore_limit'], int) or kwargs['semaphore_limit'] <= 0):
            raise ValueError(
                'Invalid configuration: "semaphore_limit" must be a positive integer, indicating the maximum number of concurrent asynchronous operations permitted.'
            )

        self._semaphore_limit = kwargs.get('semaphore_limit', 5)
        self._base_url = DEFAULT_VNDIRECT_FUNDAMENTAL_INDEX_BASE_URL
        self._domain = DEFAULT_VNDIRECT_DOMAIN
        self._scraper = VistockVnDirectFundamentalIndexScraper()
        self._parser = VistockVnDirectFundamentalIndexParser()
        self._semaphore = asyncio.Semaphore(self._semaphore_limit)

    @property
    def timeout(self) -> float:
        return self._timeout
    
    @timeout.setter
    def timeout(self, value: int) -> None:
        if value <= 0:
            raise ValueError(
                'Invalid value: "timeout" must be a positive integer greater than zero.'
            )
        self._timeout = value

    def search(self, code: str) -> StandardVnDirectFundamentalIndexSearchResults:
        try:
            if not VistockValidator.validate_code(code):
                raise ValueError(
                    'Invalid code: "code" must be a non-empty alphanumeric string with exactly 3 characters representing the stock code. Please ensure that the code is specified correctly.'
                )
            
            results: List[List[Dict[str, Any]]] = []
            
            urls = self._parser.parse_url_path(code=code)
            for url in urls:
                url = f"{self._base_url}{url}"
                data: List[Dict[str, Any]] = self._scraper.fetch(url).get('data', [])

                if not data:
                    raise ValueError(
                    'No data found for the given parameters. Please check the code, start date, and end date to ensure they are correct and that data exists for the specified range.'
                )
                
                results.append(data)

            merged_results = [item for result in results for item in result]

            field_map = {
                "MARKETCAP": "marketcap",
                "NMVOLUME_AVG_CR_10D": "nm_volume_avg_cr_10d",
                "PRICE_HIGHEST_CR_52W": "price_highest_cr_52w",
                "PRICE_LOWEST_CR_52W": "price_lowest_cr_52w",
                "OUTSTANDING_SHARES": "outstanding_shares",
                "FREEFLOAT": "freefloat",
                "BETA": "beta",
                "PRICE_TO_EARNINGS": "price_to_earnings",
                "PRICE_TO_BOOK": "price_to_book",
                "ROAE_TR_AVG5Q": "roae_tr_avg_5q",
                "ROAA_TR_AVG5Q": "roaa_tr_avg_5q",
                "DIVIDEND_YIELD": "dividend_yield",
                "EPS_TR": "eps_tr",
                "BVPS_CR": "bvps_cr"
            }

            model_data: Dict[str, float] = {}
            for item in merged_results:
                key = field_map.get(item["ratioCode"])
                if key:
                    model_data[key] = item["value"]

            return StandardVnDirectFundamentalIndexSearchResults(**model_data)
        
        except Exception:
            logger.error("An unexpected error occurred during the search operation.", exc_info=True)
            raise

    async def async_search(self, code: str) -> StandardVnDirectFundamentalIndexSearchResults:
        try:
            if not VistockValidator.validate_code(code):
                raise ValueError(
                    'Invalid code: "code" must be a non-empty alphanumeric string with exactly 3 characters representing the stock code. Please ensure that the code is specified correctly.'
                )
            
            results: List[List[Dict[str, Any]]] = []
            
            urls = self._parser.parse_url_path(code=code)
            for url in urls:
                url = f"{self._base_url}{url}"
                response = await self._scraper.async_fetch(url)
                data: List[Dict[str, Any]] = response.get('data', [])

                if not data:
                    raise ValueError(
                    'No data found for the given parameters. Please check the code, start date, and end date to ensure they are correct and that data exists for the specified range.'
                )
                
                results.append(data)

            merged_results = [item for result in results for item in result]

            field_map = {
                "MARKETCAP": "marketcap",
                "NMVOLUME_AVG_CR_10D": "nm_volume_avg_cr_10d",
                "PRICE_HIGHEST_CR_52W": "price_highest_cr_52w",
                "PRICE_LOWEST_CR_52W": "price_lowest_cr_52w",
                "OUTSTANDING_SHARES": "outstanding_shares",
                "FREEFLOAT": "freefloat",
                "BETA": "beta",
                "PRICE_TO_EARNINGS": "price_to_earnings",
                "PRICE_TO_BOOK": "price_to_book",
                "ROAE_TR_AVG5Q": "roae_tr_avg_5q",
                "ROAA_TR_AVG5Q": "roaa_tr_avg_5q",
                "DIVIDEND_YIELD": "dividend_yield",
                "EPS_TR": "eps_tr",
                "BVPS_CR": "bvps_cr"
            }

            model_data: Dict[str, float] = {}
            for item in merged_results:
                key = field_map.get(item["ratioCode"])
                if key:
                    model_data[key] = item["value"]

            return StandardVnDirectFundamentalIndexSearchResults(**model_data)
        
        except Exception:
            logger.error("An unexpected error occurred during the search operation.", exc_info=True)
            raise