# TalkAbout

[![PyPI version](https://badge.fury.io/py/talkabout.svg)](https://badge.fury.io/py/talkabout)

AI-powered object query proxy using Claude AI. Query any Python object using natural language and get Python code executed automatically.

## Installation

```bash
pip install talkabout
```

## Setup

You'll need an Anthropic API key. Set it as an environment variable:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Or pass it directly when creating a Talk instance:

```python
from talkabout import Talk
talk = Talk(my_object, api_key="your-api-key-here")
```

## Usage

A simple example:

```python
import numpy as np
from talkabout import Talk

x = np.random.uniform(size=50)

talk = Talk(x)
talk('90th percentile')

# printed output
Executing code: np.percentile(obj, 90)

Out[1]: np.float64(0.8442100946036629)
```

A more complicated example - inspect financials of a company using Yahoo Finance API:

```python
import yfinance as yf
from talkabout import Talk

pypl = yf.Ticker('PYPL')

talk = Talk(pypl)
talk('qoq Oper CF over debt; use .loc')

# printed output
Executing code: pypl.quarterly_cash_flow.loc['Operating Cash Flow'].pct_change() / pypl.quarterly_balancesheet.loc['Total Debt']

Out[6]:
2025-03-31             NaN
2024-12-31    1.076823e-10
2024-09-30   -3.265984e-11
2024-06-30   -5.669014e-12
2024-03-31    2.654644e-11
2023-12-31             NaN
dtype: float64
```

