from vistock.core.models import (
    StandardVnDirectStockIndexSearchResults, 
    AdvancedVnDirectStockIndexSearchResults,
    StandardVnDirectFundamentalIndexSearchResults,
    Standard24HMoneyStockSectionSearchResults,
    StandardVnDirectFinancialModelSearchResults,
    StandardVnDirectFinancialStatementsIndexSearchResults
)
from vistock.core.enums import (
    Vistock24HMoneyIndustryCategory,
    Vistock24HMoneyFloorCategory,
    Vistock24HMoneyCompanyCategory,
    Vistock24HMoneyLetterCategory,
    VistockVnDirectFinancialModelsCategory,
    VistockVnDirectReportTypeCategory
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

class IVistockVnDirectFinancialModelsSearch(Protocol):
    def search(
        self,
        code: str,
        model_type: Union[VistockVnDirectFinancialModelsCategory, str] = 'all'
    ) -> StandardVnDirectFinancialModelSearchResults:
        ...

class AsyncIVistockVnDirectFinancialModelsSearch(Protocol):
    async def async_search(
        self,
        code: str,
        model_type: Union[VistockVnDirectFinancialModelsCategory, str] = 'all'
    ) -> StandardVnDirectFinancialModelSearchResults:
        ...

class IVistockVnDirectFinancialStatementsIndexSearch(Protocol):
    def search(
        self,
        code: str,
        start_year: int = 2000,
        end_year: int = datetime.now().year,
        report_type: Union[VistockVnDirectReportTypeCategory, str] = 'ANNUAL',
        model_type: Union[VistockVnDirectFinancialModelsCategory, str] = 'all'
    ) -> StandardVnDirectFinancialStatementsIndexSearchResults:
        ...

class AsyncIVistockVnDirectFinancialStatementsIndexSearch(Protocol):
    async def async_search(
        self,
        code: str,
        start_year: int = 2000,
        end_year: int = datetime.now().year,
        report_type: Union[VistockVnDirectReportTypeCategory, str] = 'ANNUAL',
        model_type: Union[VistockVnDirectFinancialModelsCategory, str] = 'all'
    ) -> StandardVnDirectFinancialStatementsIndexSearchResults:
        ...

class IVistock24HMoneyStockSectionSearch(Protocol):
    def search(
        self,
        industry: Union[Vistock24HMoneyIndustryCategory, str] = 'all',
        floor: Union[Vistock24HMoneyFloorCategory, str] = 'all',
        company_type: Union[Vistock24HMoneyCompanyCategory, str] = 'all',
        letter: Union[Vistock24HMoneyLetterCategory, str] = 'all',
        limit: int = 2000
    ) -> Standard24HMoneyStockSectionSearchResults:
        ...

class AsyncIVistock24HMoneyStockSectionSearch(Protocol):
    async def async_search(
        self,
        industry: Union[Vistock24HMoneyIndustryCategory, str] = 'all',
        floor: Union[Vistock24HMoneyFloorCategory, str] = 'all',
        company_type: Union[Vistock24HMoneyCompanyCategory, str] = 'all',
        letter: Union[Vistock24HMoneyLetterCategory, str] = 'all',
        limit: int = 2000 
    ) -> Standard24HMoneyStockSectionSearchResults:
        ...