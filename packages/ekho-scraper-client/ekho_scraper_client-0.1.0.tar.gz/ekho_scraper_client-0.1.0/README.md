# ekho-scraper-client

A Python client for the Ekho scraping service.

## Installation

```bash
pip install ekho-scraper-client
```

## Usage

```python
from ekho import scrape

result = scrape("https://www.ashgrove.com/locations")
print(result)
```

### Environment

You can override the default service endpoint by setting the `EKHO_SCRAPER_ENDPOINT` environment variable:

```bash
export EKHO_SCRAPER_ENDPOINT="https://my.internal.endpoint/scrape"
```

## Development

Build distribution packages:

```bash
pip install --upgrade build twine
python -m build
```

Publish to PyPI:

```bash
twine upload dist/*
```
