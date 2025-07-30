# ekho-scraper-client

A Python client for the Ekho scraping service.

## Installation

```bash
pip install ekho-scraper-client
```

## Usage

```python
from ekho import scrape, subpages

result = scrape("https://www.ashgrove.com/locations")
print(result)

subpages_result = subpages("https://www.ashgrove.com/locations")
print(subpages_result)
```

### Environment

You can override the default service endpoints by setting the following environment variables:

```bash
export EKHO_SCRAPER_ENDPOINT="https://my.internal.endpoint/scrape"
export EKHO_SUBPAGES_ENDPOINT="https://my.internal.endpoint/subpages"
```

## Development

Build distribution packages:

```bash
pip install --upgrade build twine
python -m build
```

Publish to PyPI:

```bash
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="<your-api-token>"

twine upload dist/*
```
