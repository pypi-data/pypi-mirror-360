# Econpapers

A simple package to retrieve published papers in economics from [RePEC's EconPapers platform](https://econpapers.repec.org/).

## Installing & using

To install, copy and paste this script:

```bash
pip install econpapers
```

Then import the package:

```python
import econpapers as econ
```

You can then use the package to retrieve published papers' metadata (title, authors, year, abstract if provided, JEL codes if provided and link to the page within the site), by inputting a list like this:

```python
econ.papers_dataframe(["Econometrica"])
```
or 

```python
econ.papers_dataframe(["Econometrica", "Quarterly Journal of Economics"])
```

and the output will be saved as a [Pandas](https://github.com/pandas-dev/pandas) DataFrame.

(So far, only lists are accepted, and journal names are case-sensitive. Apologies!)



