from vistock.core.models import (
    StandardVnDirectStockIndexSearchResults, 
    AdvancedVnDirectStockIndexSearchResults,
    StandardVnDirectFundamentalIndexSearchResults
)
from typing import Union, Protocol, Literal
from datetime import datetime

class IVistockVnDirectStockIndexSearch(Protocol):
    def search(
        self, 
        code: str,
        start_date: str = '2012-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        resolution: Literal['day', 'week', 'month', 'year'] = 'day',
        advanced: bool = True,
        ascending: bool = False
    ) -> Union[StandardVnDirectStockIndexSearchResults, AdvancedVnDirectStockIndexSearchResults]:
        ...

class AsyncIVistockVnDirectStockIndexSearch(Protocol):
    async def async_search(
        self, 
        code: str,
        start_date: str = '2012-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        resolution: Literal['day', 'week', 'month', 'year'] = 'day',
        advanced: bool = True,
        ascending: bool = False
    ) -> Union[StandardVnDirectStockIndexSearchResults, AdvancedVnDirectStockIndexSearchResults]:
        ...

class IVistockVnDirectFundamentalIndexSearch(Protocol):
    def search(
        self,
        code: str
    ) -> StandardVnDirectFundamentalIndexSearchResults:
        ...

class AsyncIVistockVnDirectFundamentalIndexSearch(Protocol):
    async def async_search(
        self,
        code: str
    ) -> StandardVnDirectFundamentalIndexSearchResults:
        ...