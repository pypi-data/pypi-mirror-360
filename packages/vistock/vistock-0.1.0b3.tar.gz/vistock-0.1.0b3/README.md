# VISTOCK

**Vistock** is an open-source library focused on searching, retrieving, and analyzing Vietnamese stock market data. It aims to provide robust tools that support developers, researchers, and AI agents in accessing and processing financial market information from Vietnam.

> **Note**: Vistock is under active development. Features may be incomplete or subject to change. Contributions, suggestions, and bug reports are welcome and highly appreciated!

## Disclaimer & Terms of Use ‼️

This library is provided for **educational and research purposes only**. You are solely responsible for how you use it. Before scraping any website, you must ensure that your actions comply with all applicable laws and the website’s own policies — including their **Terms of Service** and `robots.txt` directives. Many websites explicitly prohibit automated access. The authors and contributors are not responsible for any misuse or legal issues arising from the use of this tool. Always scrape ethically, respectfully, and within legal boundaries.

## Responsible Scraping ‼️

Please be respectful of the websites you interact with. Always use appropriate rate limiting and avoid sending excessive requests. Scraping should never disrupt or degrade the performance of a website. Generating unreasonable traffic may not only lead to IP bans but could also violate legal or ethical standards. Respect the site's resources, policies, and the efforts of its creators.

## Supported Websites

- **Vndirect**
- **Vietstock**
- **24hmoney**
- *more coming soon...*

## Installation

```bash
pip install vistock
```

## Quick Start
```python
from vistock.modules.vndirect.search import VistockVnDirectStockIndexSearch
import asyncio
import json

async def main():
    search = VistockVnDirectStockIndexSearch()
    
    data = search.search(
        code="ACB",
        start_date="2025-06-20",
        end_date="2025-06-28",
        resolution="day",
        advanced=False,
        ascending=False
    )

    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(data.model_dump(), file, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    asyncio.run(main())
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache 2.0 - see the `LICENSE` file for details.

