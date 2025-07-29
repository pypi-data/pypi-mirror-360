from vistock.core.constants import (
    DEFAULT_24HMONEY_BASE_URL,
    DEFAULT_24HMONEY_DOMAIN,
    DEFAULT_TIMEOUT
)
from vistock.core.models import (
    Standard24HMoneyStockSection,
    Standard24HMoneyStockSectionSearchResults
)
from vistock.core.enums import (
    Vistock24HMoneyIndustryCategory,
    Vistock24HMoneyFloorCategory,
    Vistock24HMoneyCompanyCategory,
    Vistock24HMoneyLetterCategory
)
from vistock.modules._24hmoney.scrapers import Vistock24HMoneyStockSectionScraper
from vistock.modules._24hmoney.parsers import Vistock24HMoneyStockSectionParser
from vistock.core.utils import VistockValidator, VistockNormalizator, VistockMapper
from typing import List, Dict, Union, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

class Vistock24HMoneyStockSectionSearch:
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
        self._base_url = DEFAULT_24HMONEY_BASE_URL
        self._domain = DEFAULT_24HMONEY_DOMAIN
        self._scraper = Vistock24HMoneyStockSectionScraper()
        self._parser = Vistock24HMoneyStockSectionParser()
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

    def search(
        self,
        industry: Union[Vistock24HMoneyIndustryCategory, str] = 'all',
        floor: Union[Vistock24HMoneyFloorCategory, str] = 'all',
        company_type: Union[Vistock24HMoneyCompanyCategory, str] = 'all',
        letter: Union[Vistock24HMoneyLetterCategory, str] = 'all',
        limit: int = 2000
    ) -> Standard24HMoneyStockSectionSearchResults:
        try:
            if industry != 'all':
                if not VistockValidator.validate_enum_value(industry, Vistock24HMoneyIndustryCategory):
                    raise ValueError(f'"{industry}" is not a recognized industry. Use a valid enum name or code.')
                industry_code = VistockNormalizator.normalize_enum_value(industry, Vistock24HMoneyIndustryCategory)
            else:
                industry_code = 'all'

            if floor != 'all':
                if not VistockValidator.validate_enum_value(floor, Vistock24HMoneyFloorCategory):
                    raise ValueError(f'"{floor}" is not a valid floor. Please use a correct market floor name or code.')
                floor_code = VistockNormalizator.normalize_enum_value(floor, Vistock24HMoneyFloorCategory)
            else:
                floor_code = 'all'

            if company_type != 'all':
                if not VistockValidator.validate_enum_value(company_type, Vistock24HMoneyCompanyCategory):
                    raise ValueError(f'"{company_type}" is not a valid company type. Use a defined category or symbol.')
                company_code = VistockNormalizator.normalize_enum_value(company_type, Vistock24HMoneyCompanyCategory)
            else:
                company_code = 'all'

            if letter != 'all':
                if not VistockValidator.validate_enum_value(letter, Vistock24HMoneyLetterCategory):
                    raise ValueError(f'"{letter}" is not a valid letter. Only A-Z are accepted.')
                letter_code = VistockNormalizator.normalize_enum_value(letter, Vistock24HMoneyLetterCategory)
            else:
                letter_code = 'all'

            url = f'{self._base_url}{self._parser.parse_url_path(industry_code=industry_code, floor_code=floor_code, company_code=company_code, letter_code=letter_code, limit=limit)}'
            data: List[Dict[str, Any]] = self._scraper.fetch(url=url).get('data', [])['data']

            results: List[Standard24HMoneyStockSection] = []
            for item in data:
                icb_name_vi = item.get('icb_name_vi', '')
                try:
                    icb_name_en = VistockMapper.map_english_section(vn_section=icb_name_vi)
                except ValueError:
                    icb_name_en = ''

                result = Standard24HMoneyStockSection(
                    code=item.get('symbol', '') or '',
                    company_name=item.get('company_name', '') or '',
                    tfloor=item.get('floor', '') or '',
                    company_type=item.get('fiingroup_com_type_code', '') or '',
                    icb_name_vi=icb_name_vi or '',
                    icb_name_en=icb_name_en,
                    listed_share_vol=item.get('listed_share_vol', 0) or 0,
                    fiingroup_icb_code=item.get('fiingroup_icb_code', 0) or 0
                )
                results.append(result)
            
            return Standard24HMoneyStockSectionSearchResults(results=results, total_results=len(data))

        except Exception:
            logger.error('An unexpected error occurred during the search operation.', exc_info=True)
            raise

class AsyncVistock24HMoneyStockSectionSearch:
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
        self._base_url = DEFAULT_24HMONEY_BASE_URL
        self._domain = DEFAULT_24HMONEY_DOMAIN
        self._scraper = Vistock24HMoneyStockSectionScraper()
        self._parser = Vistock24HMoneyStockSectionParser()
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
        
    async def async_search(
        self,
        industry: Union[Vistock24HMoneyIndustryCategory, str] = 'all',
        floor: Union[Vistock24HMoneyFloorCategory, str] = 'all',
        company_type: Union[Vistock24HMoneyCompanyCategory, str] = 'all',
        letter: Union[Vistock24HMoneyLetterCategory, str] = 'all',
        limit: int = 2000
    ) -> Standard24HMoneyStockSectionSearchResults:
        try:
            if industry != 'all':
                if not VistockValidator.validate_enum_value(industry, Vistock24HMoneyIndustryCategory):
                    raise ValueError(f'"{industry}" is not a recognized industry. Use a valid enum name or code.')
                industry_code = VistockNormalizator.normalize_enum_value(industry, Vistock24HMoneyIndustryCategory)
            else:
                industry_code = 'all'

            if floor != 'all':
                if not VistockValidator.validate_enum_value(floor, Vistock24HMoneyFloorCategory):
                    raise ValueError(f'"{floor}" is not a valid floor. Please use a correct market floor name or code.')
                floor_code = VistockNormalizator.normalize_enum_value(floor, Vistock24HMoneyFloorCategory)
            else:
                floor_code = 'all'

            if company_type != 'all':
                if not VistockValidator.validate_enum_value(company_type, Vistock24HMoneyCompanyCategory):
                    raise ValueError(f'"{company_type}" is not a valid company type. Use a defined category or symbol.')
                company_code = VistockNormalizator.normalize_enum_value(company_type, Vistock24HMoneyCompanyCategory)
            else:
                company_code = 'all'

            if letter != 'all':
                if not VistockValidator.validate_enum_value(letter, Vistock24HMoneyLetterCategory):
                    raise ValueError(f'"{letter}" is not a valid letter. Only A-Z are accepted.')
                letter_code = VistockNormalizator.normalize_enum_value(letter, Vistock24HMoneyLetterCategory)
            else:
                letter_code = 'all'

            url = f'{self._base_url}{self._parser.parse_url_path(industry_code=industry_code, floor_code=floor_code, company_code=company_code, letter_code=letter_code, limit=limit)}'

            async with self._semaphore:
                raw_response = await self._scraper.async_fetch(url=url)  # This line assumes your scraper is async

            data: List[Dict[str, Any]] = raw_response.get('data', [])['data']

            results: List[Standard24HMoneyStockSection] = []
            for item in data:
                icb_name_vi = item.get('icb_name_vi', '')
                try:
                    icb_name_en = VistockMapper.map_english_section(vn_section=icb_name_vi)
                except ValueError:
                    icb_name_en = ''

                result = Standard24HMoneyStockSection(
                    code=item.get('symbol', '') or '',
                    company_name=item.get('company_name', '') or '',
                    tfloor=item.get('floor', '') or '',
                    company_type=item.get('fiingroup_com_type_code', '') or '',
                    icb_name_vi=icb_name_vi or '',
                    icb_name_en=icb_name_en,
                    listed_share_vol=item.get('listed_share_vol', 0) or 0,
                    fiingroup_icb_code=item.get('fiingroup_icb_code', 0) or 0
                )
                results.append(result)

            return Standard24HMoneyStockSectionSearchResults(results=results, total_results=len(data))

        except Exception:
            logger.error('An unexpected error occurred during the search operation.', exc_info=True)
            raise