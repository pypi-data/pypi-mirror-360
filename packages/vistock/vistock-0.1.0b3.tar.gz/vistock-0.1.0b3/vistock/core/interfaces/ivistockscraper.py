from typing import Dict, Any

class IVistockVnDirectStockIndexScraper:
    def fetch(self, url: str) -> Dict[str, Any]:
        ...

class AsyncIVistockVnDirectStockIndexScraper:
    async def async_fetch(self, url: str) -> Dict[str, Any]:
        ...

class IVistockVnDirectFundamentalIndexScraper:
    def fetch(self, url: str) -> Dict[str, Any]:
        ...

class AsyncIVistockVnDirectFundamentalIndexScraper:
    async def async_fetch(self, url: str) -> Dict[str, Any]:
        ...

class IVistockVnDirectFinancialModelsScraper:
    def fetch(self, url: str) -> Dict[str, Any]:
        ...

class AsyncIVistockVnDirectFinancialModelsScraper:
    async def async_fetch(self, url: str) -> Dict[str, Any]:
        ...

class IVistockVnDirectFinancialStatementsIndexScraper:
    def fetch(self, url: str) -> Dict[str, Any]:
        ...

class AsyncIVistockVnDirectFinancialStatementsIndexScraper:
    async def async_fetch(self, url: str) -> Dict[str, Any]:
        ...

class IVistock24HMoneyStockSectionScraper:
    def fetch(self, url: str) -> Dict[str, Any]:
        ...

class AsyncIVistock24HMoneyStockSectionScraper:
    async def async_fetch(self, url: str) -> Dict[str, Any]:
        ...