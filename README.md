# Scraper: Smart CJM - Online-Terminvereinbarung

Smart CJM seems to be a provider of online tools for public authorities. One of those tools is for
[Online-Terminvereinbarung](https://smart-cjm.com/public-authorities/online-terminvereinbarung/) i.e. to find an
appointment. This scraper allows you to receive notifications based of off slots opening up on a short notice.

## Installation

```bash
git clone https://github.com/larsborn/smart-cjm-scraper.git
cd smart-cjm-scraper
# create virtual environment
pip install -r requirements.txt
```

## Execution (Stadt Bonn)

The following will generate output if and only if there's an appointment free to do "Abmeldung" at the
"Dienstleistungszentrum" within the next 3 days:

```bash
export PYTHONPATH=.
export BASE_URL="https://termine.bonn.de/m/dlz/extern/calendar"
export TENANT_UID="b91bb67b-15cf-44df-ab0b-96ebe25c1ae3"
python smart_cjm/scraper.py --days 3 "Abmeldung" "Dienstleistungszentrum"
```
