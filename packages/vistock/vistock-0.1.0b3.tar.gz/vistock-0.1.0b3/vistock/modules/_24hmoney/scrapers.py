from vistock.core.constants import (
    DEFAULT_24HMONEY_BASE_URL, DEFAULT_24HMONEY_DOMAIN, DEFAULT_24HMONEY_HEADERS,
    DEFAULT_TIMEOUT, DEFAULT_TIMEOUT_CONNECT
)
from vistock.core.interfaces.ivistockscraper import (
    IVistock24HMoneyStockSectionScraper,
    AsyncIVistock24HMoneyStockSectionScraper
)
from vistock.core.utils import VistockValidator
from typing import Dict, Any
import tenacity
import httpx

class Vistock24HMoneyStockSectionScraper(IVistock24HMoneyStockSectionScraper, AsyncIVistock24HMoneyStockSectionScraper):
    def __init__(self, **kwargs: Any) -> None:
        self._base_url = DEFAULT_24HMONEY_BASE_URL
        self._domain = DEFAULT_24HMONEY_DOMAIN

        timeout = kwargs.get('timeout', DEFAULT_TIMEOUT)
        timeout_connect = kwargs.get('timeout_connect', DEFAULT_TIMEOUT_CONNECT)

        if not isinstance(timeout, (int, float)) or not isinstance(timeout_connect, (int, float)):
            raise ValueError(
                'Invalid timeout configuration: both "timeout" and "timeout_connect" must be numeric types (int or float).'
            )
        
        if timeout <= 0 or timeout_connect <= 0:
            raise ValueError(
                'Invalid timeout configuration: both "timeout" and "timeout_connect" must be greater than zero to ensure proper request handling.'
            )
        
        if timeout < timeout_connect:
            raise ValueError(
                'Invalid timeout configuration: the overall "timeout" value must be greater than or equal to "timeout_connect" to avoid premature termination.'
            )
        
        self._timeout = httpx.Timeout(
            timeout=timeout,
            connect=timeout_connect
        )

        headers: Dict[str, Any] = kwargs.get('headers', DEFAULT_24HMONEY_HEADERS)

        self._headers = headers

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=2, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
        retry=tenacity.retry_if_exception_type(httpx.HTTPStatusError)
    )
    def fetch(self, url: str):
        if not VistockValidator.validate_url_with_domain(url, self._domain):
            raise ValueError(
                f'Invalid URL: "{url}". The URL must belong to the expected domain "{self._domain}" to ensure proper validation and access control.'
            ) 
                
        with httpx.Client(timeout=self._timeout) as client:
            response = client.get(url, headers=self._headers)
            response.raise_for_status()

        return response.json()
    
    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=2, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
        retry=tenacity.retry_if_exception_type(httpx.HTTPStatusError)
    )
    async def async_fetch(self, url: str):
        if not VistockValidator.validate_url_with_domain(url, self._domain):
            raise ValueError(
                f'Invalid URL: "{url}". The provided URL must belong to the expected domain "{self._domain}" '
                "to ensure source integrity and proper routing within the system."
            )
        
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url, headers=self._headers)
            response.raise_for_status()

        return response.json()
    


