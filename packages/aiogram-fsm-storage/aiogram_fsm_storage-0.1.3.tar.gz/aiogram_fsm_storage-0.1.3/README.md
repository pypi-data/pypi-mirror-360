# aiogram-fsm-storage

[![PyPI](https://img.shields.io/pypi/v/aiogram-fsm-storage)](https://pypi.org/project/aiogram-fsm-storage/)
[![Python Versions](https://img.shields.io/pypi/pyversions/aiogram-fsm-storage)](https://pypi.org/project/aiogram-fsm-storage/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Custom file-based and SQLite-based storage for [Aiogram 3.x](https://github.com/aiogram/aiogram), 
built from scratch without external dependencies.

## Features

- ✅ JSON, Pickle, and SQLite storage implementations
- ✅ Fully async structure
- ✅ Compatible with Dispatcher from Aiogram 3.x
- ✅ Simple and lightweight
- ✅ MIT Licensed & production-ready

## Installation

```bash
pip install aiogram-fsm-storage
```

## Usage

```python
from aiogram import Dispatcher
from aiogram_fsm_storage import JSONStorage  # or PickleStorage, SQLiteStorage

dp = Dispatcher(storage=JSONStorage(path="states.json"))
```
