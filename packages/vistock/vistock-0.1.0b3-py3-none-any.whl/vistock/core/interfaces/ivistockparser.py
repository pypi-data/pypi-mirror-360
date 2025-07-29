from vistock.core.enums import (
    Vistock24HMoneyIndustryCategory,
    Vistock24HMoneyFloorCategory,
    Vistock24HMoneyCompanyCategory,
    Vistock24HMoneyLetterCategory
)
from typing import List, Union, Protocol
from datetime import datetime

class IViStockVnDirectStockIndexParser(Protocol):
    def parse_url_path(
        self,
        code: str,
        start_date: str = '2012-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        limit: int = 1
    ) -> str:
        ...

class IVistockVnDirectFundamentalIndexParser(Protocol):
    def parse_url_path(
        self,
        code: str
    ) -> List[str]:
        ...

class IVistockVnDirectFinancialModelsParser(Protocol):
    def parse_url_path(
        self,
        code: str,
        model_type_code: str,
        limit: int = 2000
    ) -> List[str]:
        ...

class IVistockVnDirectFinancialStatementsIndexParser(Protocol):
    def parse_url_path(
        self,
        code: str,
        start_year: int = 2000,
        end_year: int = datetime.now().year,
        report_type_code: str = 'ANNUAL',
        model_type_code: str = 'all',
        limit: int = 10000
    ) -> List[str]:
        ...

class IVistock24HMoneyStockSectionParser(Protocol):
    def parse_url_path(
        self,
        industry_code: Union[Vistock24HMoneyIndustryCategory, str] = 'all',
        floor_code: Union[Vistock24HMoneyFloorCategory, str] = 'all',
        company_code: Union[Vistock24HMoneyCompanyCategory, str] = 'all',
        letter_code: Union[Vistock24HMoneyLetterCategory, str] = 'all',
        limit: int = 2000
    ) -> str:
        ...