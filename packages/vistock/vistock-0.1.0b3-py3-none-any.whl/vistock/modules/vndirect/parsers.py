from vistock.core.interfaces.ivistockparser import (
    IViStockVnDirectStockIndexParser,
    IVistockVnDirectFundamentalIndexParser,
    IVistockVnDirectFinancialModelsParser,
    IVistockVnDirectFinancialStatementsIndexParser
)
from vistock.core.constants import DEFAULT_VNDIRECT_DOMAIN
from vistock.core.enums import VistockVnDirectFinancialModelsCategory
from vistock.core.utils import VistockValidator, VistockGenerator
from urllib.parse import urlencode
from datetime import datetime
from typing import List, Dict, Any

class VistockVnDirectStockIndexParser(IViStockVnDirectStockIndexParser):
    def __init__(self):
        self._domain = DEFAULT_VNDIRECT_DOMAIN

    def parse_url_path(
        self,
        code: str,
        start_date: str = '2012-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        limit: int = 1
    ) -> str:
        if not VistockValidator.validate_code(code=code):
            raise ValueError(
                'Invalid code: "code" must be a non-empty alphanumeric string with exactly 3 characters representing the stock code. Please ensure that the code is specified correctly.'
            )

        if limit < 0:
            raise ValueError(
                'Invalid limit: "limit" must be a positive integer greater than zero to ensure proper pagination and data retrieval.'
            )
        
        if limit == 0:
            limit += 1

        query_parts = [f'code:{code}']

        if not VistockValidator.validate_date_range(start_date=start_date, end_date=end_date):
            raise ValueError(
                'Invalid date range: "start_date" must be earlier than "end_date". Please ensure that the start date precedes the end date to maintain a valid chronological order.'
            )

        if VistockValidator.validate_date_format(date_str=start_date):
            query_parts.append(f'date:gte:{start_date}')
            
        if VistockValidator.validate_date_format(date_str=end_date):
            query_parts.append(f'date:lte:{end_date}')

        q_param = '~'.join(query_parts)

        query_params : Dict[str, Any] = {
            'sort': 'date',
            'q': q_param,
            'size': limit,
            'page': 1
        }

        return f'?{urlencode(query_params)}'
            
class VistockVnDirectFundamentalIndexParser(IVistockVnDirectFundamentalIndexParser):
    def __init__(self):
        self._domain = DEFAULT_VNDIRECT_DOMAIN
        self._url_templates = [
            '?filter=ratioCode:MARKETCAP,NMVOLUME_AVG_CR_10D,PRICE_HIGHEST_CR_52W,PRICE_LOWEST_CR_52W,OUTSTANDING_SHARES,FREEFLOAT,BETA,PRICE_TO_EARNINGS,PRICE_TO_BOOK,DIVIDEND_YIELD,BVPS_CR,&where=code:{code}&order=reportDate&fields=ratioCode,value',
            '?filter=ratioCode:ROAE_TR_AVG5Q,ROAA_TR_AVG5Q,EPS_TR,&where=code:{code}&order=reportDate&fields=ratioCode,value'
        ]

    def parse_url_path(self, code: str) -> List[str]:
        if not VistockValidator.validate_code(code=code):
            raise ValueError(
                'Invalid code: "code" must be a non-empty alphanumeric string with exactly 3 characters representing the stock code. Please ensure that the code is specified correctly.'
            )
        
        return [template.format(code=code) for template in self._url_templates]
    
class VistockVnDirectFinancialModelsParser(IVistockVnDirectFinancialModelsParser):
    def __init__(self):
        self._domain = DEFAULT_VNDIRECT_DOMAIN
        self._url_template = '?sort=displayOrder:asc&q=codeList:{code}~modelType:{model_type_code}~note:TT199/2014/TT-BTC,TT334/2016/TT-BTC,TT49/2014/TT-NHNN,TT202/2014/TT-BTC~displayLevel:0,1,2,3&size={limit}'

    def parse_url_path(
        self, 
        code: str, 
        model_type_code: str, 
        limit: int = 2000
    ) -> List[str]:
        if not VistockValidator.validate_code(code=code):
            raise ValueError(
                'Invalid code: "code" must be a non-empty alphanumeric string with exactly 3 characters representing the stock code. Please ensure that the code is specified correctly.'
            )
        
        urls: List[str] = []

        if model_type_code == 'all':
            for category in VistockVnDirectFinancialModelsCategory:
                if category.value == 'all':
                    continue

                url = self._url_template.format(
                    code=code,
                    model_type_code=category.value,
                    limit=limit
                )
                urls.append(f'{url}')

            return urls
        else:
            url = self._url_template.format(
                code=code,
                model_type_code=model_type_code,
                limit=limit
            )
            urls.append(f'{url}')

            return urls
    
class VistockVnDirectFinancialStatementsIndexParser(IVistockVnDirectFinancialStatementsIndexParser):
    def __init__(self):
        self._domain = DEFAULT_VNDIRECT_DOMAIN
        self._url_template = '?q=code:{code}~reportType:{report_type_code}~modelType:{model_type_code}~fiscalDate:{fiscal_date}&sort=fiscalDate&size={limit}'

    def parse_url_path(
        self,
        code: str,
        start_year: int = 2000,
        end_year: int = datetime.now().year,
        report_type_code: str = 'ANNUAL',
        model_type_code: str = 'all',
        limit: int = 10000
    ) -> List[str]:
        if not VistockValidator.validate_code(code=code):
            raise ValueError(
                'Invalid code: "code" must be a non-empty alphanumeric string with exactly 3 characters representing the stock code. Please ensure that the code is specified correctly.'
            )
        
        if report_type_code == 'QUARTER':
            fiscal_date = VistockGenerator.generate_quarterly_dates(start_year=start_year, end_year=end_year)

        fiscal_date = VistockGenerator.generate_annual_dates(start_year=start_year, end_year=end_year)

        urls: List[str] = []

        if model_type_code == 'all':
            for category in VistockVnDirectFinancialModelsCategory:
                if category.value == 'all':
                    continue

                url = self._url_template.format(
                    code=code,
                    report_type_code=report_type_code,
                    model_type_code=category.value,
                    fiscal_date=fiscal_date,
                    limit=limit
                )
                urls.append(f'{url}')

            return urls
        else:
            url = self._url_template.format(
                code=code,
                report_type_code=report_type_code,
                model_type_code=model_type_code,
                fiscal_date=fiscal_date,
                limit=limit
            )
            urls.append(f'{url}')

            return urls