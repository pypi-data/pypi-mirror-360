from vistock.core.interfaces.ivistockparser import IVistock24HMoneyStockSectionParser
from vistock.core.constants import DEFAULT_24HMONEY_DOMAIN
from vistock.core.enums import (
    Vistock24HMoneyIndustryCategory,
    Vistock24HMoneyFloorCategory,
    Vistock24HMoneyCompanyCategory,
    Vistock24HMoneyLetterCategory
)
from typing import Union

class Vistock24HMoneyStockSectionParser(IVistock24HMoneyStockSectionParser):
    def __init__(self):
        self._domain = DEFAULT_24HMONEY_DOMAIN

    def parse_url_path(
        self,
        industry_code: Union[Vistock24HMoneyIndustryCategory, str] = 'all',
        floor_code: Union[Vistock24HMoneyFloorCategory, str] = 'all',
        company_code: Union[Vistock24HMoneyCompanyCategory, str] = 'all',
        letter_code: Union[Vistock24HMoneyLetterCategory, str] = 'all',
        limit: int = 2000
    ) -> str:
        if limit < 0:
            raise ValueError(
                'Invalid limit: "limit" must be a positive integer greater than zero to ensure proper pagination and data retrieval.'
            )
        
        if limit == 0:
            limit += 1

        return f'?&industry_code={industry_code}&floor_code={floor_code}&com_type={company_code}&letter={letter_code}&page=1&per_page={limit}'