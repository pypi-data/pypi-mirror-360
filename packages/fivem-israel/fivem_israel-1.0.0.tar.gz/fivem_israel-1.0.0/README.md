# fivem_israel

Receive live FiveM Israel votes easily in Python.

## Installation

```bash
pip install fivem_israel
```

## Usage

```python
from fivem_israel import FiveMIsrael
import asyncio

client = FiveMIsrael("your_api_key_here")

@client.event
async def on_ready():
    print("Connected to FiveM Israel Votes")

@client.event
async def on_vote(vote):
    print("New vote:", vote)

asyncio.run(client.start())
```
