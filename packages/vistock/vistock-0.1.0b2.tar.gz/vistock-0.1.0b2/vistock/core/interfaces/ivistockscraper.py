from typing import Dict, Any

class IVistockVnDirectStockIndexScraper:
    def fetch(self, url: str) -> Dict[str, Any]:
        ...

class AsyncIVistockVnDirectStockIndexScraper:
    async def async_fetch(self, url: str) -> Dict[str, Any]:
        ...

class IVistock24HMoneyScraper:
    def fetch(self, url: str) -> Dict[str, Any]:
        ...

class AsyncIVistock24HMoneyScraper:
    async def async_fetch(self, url: str) -> Dict[str, Any]:
        ...

class IVistockVnDirectFundamentalIndexScraper:
    def fetch(self, url: str) -> Dict[str, Any]:
        ...

class AsyncIVistockVnDirectFundamentalIndexScraper:
    async def async_fetch(self, url: str) -> Dict[str, Any]:
        ...