# TBGAT

Package Repository

## For Developer
**Create a venv**
```powershell
python -m venv .venv
```
**install poetry**
```powershell
pip install poetry
```

**install packages**
Install the project
```powershell
poetry install
```

Install optional dev dependencies as well
```powershell
poetry install --with dev
```

Install with extras
```powershell
poetry install --extras ner
```

# Usage

In order to run the pipelines, a database should be created. This can be done running the following command in the terminal
```powershell
tbgat init -c ukraine
```

This will set up an sqlite database called osm. 


