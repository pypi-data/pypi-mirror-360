# USDOL Wage Determination Model

Pydantic model for USDOL prevailing wage determination records


## Scripts

```bash
uv run safety scan
uv run ruff check
uv run -m pytest -vv --cov=src --cov-report=term --cov-report=xml
rm -rf dist && uv build
uv publish -t $(keyring get https://upload.pypi.org/legacy/ __token__)
```


## References

* [Wage Determintion Search on SAM.gov](https://sam.gov/search/?index=dbra)
* [Davis-Bacon and Related Acts (DBRA)](https://www.dol.gov/agencies/whd/government-contracts/construction)
* [Instructions For Completing Davis-Bacon and Related Acts Weekly Certified Payroll Form, WH-347](https://www.dol.gov/agencies/whd/forms/wh347)
https://www.dol.gov/agencies/whd/government-contracts/construction/faq


## To-Do

* Model adjustments
  * Job: add ID and perhaps an enumeration / taxonomy (US-wide or state specific?)
    * include level of journeyworker / apprentice / other?
  * Wage: taxonomy for pay types (regular, overtime, double-time, hazard), validations, more flexible fringe
  * Determination: validation for rate identifier and other fields
    * survey date before publication date
    * effective dates relation to publication date?
  * Location: Validation of state (and maybe county?), also add county identifier
  * All: descriptions
* Add docstrings and then enable "D" checks in ruff
