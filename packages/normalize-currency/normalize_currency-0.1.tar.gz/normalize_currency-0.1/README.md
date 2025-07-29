# normalize_currency

A Python package to normalize and convert multi-currency columns in pandas.

## Features
- Extract currency symbols or codes from messy strings
- Map to ISO 4217 currency codes
- Convert to a target currency using live exchange rates (`forex-python`)
- Use as a pandas accessor: `.currency.normalize(to='USD')`

## Installation

```bash
pip install git+https://github.com/your-username/normalize_currency.git
```

## Usage

```python
import pandas as pd
df = pd.DataFrame({'Pay': ['$1000', '€800', '₹70000']})
df['Pay_USD'] = df['Pay'].currency.normalize(to='USD')
```

## License
MIT