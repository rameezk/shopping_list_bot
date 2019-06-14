# Shopping List Bot

[![Build Status](https://travis-ci.com/mmphego/shopping_list_bot.svg?branch=master)](https://travis-ci.com/mmphego/shopping_list_bot)
![GitHub](https://img.shields.io/github/license/mmphego/shopping_list_bot.svg)

## The Story
Due to the [high rate of inflation](https://tradingeconomics.com/south-africa/inflation-cpi), [buying monthly groceries has become a sport](https://www.thesouthafrican.com/lifestyle/south-african-food-prices-now-more-expensive-than-the-uk/). One has to go to the ends of the world in order to good prices on the
items they need.
When doing a monthly grocery list one has to go through countless catalogues or websites to track down good prices or promotions, and that to me is very time consuming.

Overtime I started to get annoyed and decided to create a Python script that
would search for the items I have listed in a Google spreadsheet across some
of the major online shops in the country (South Africa). The script opens
various websites (Using [Selenium](https://selenium-python.readthedocs.io/)), searches for the items listed, gets the current prices and correct item name and then uploads the data to a Google Spreadsheet.
Pretty straight forward.

## Installation

1. Obtain Google API for authentication:
    *   Follow the instructions [here](https://gspread.readthedocs.io/en/latest/oauth2.html#oauth-credentials)

2. Before you install ensure that `geckodrive` for Firefox is installed.
    *   Download [geckodriver](https://github.com/mozilla/geckodriver)
        *   ```wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz```
        *   Extract: ```tar -xvzf geckodriver-v0.24.0-linux64.tar.gz```
    *   Copy `geckodriver` to /usr/local/bin

3. Now install:
    `pip install . -U`

## Usage

```bash
price_checker.py -h
usage: price_checker.py [-h] --json CLIENT_SECRET_FILE --spreadsheet_name
                        SPREADSHEET_NAME [--share-with SHARED] [--update]
                        [--loglevel LOG_LEVEL]

optional arguments:
  -h, --help            show this help message and exit
  --json CLIENT_SECRET_FILE
                        Google Json file containing secrets.
  --spreadsheet_name SPREADSHEET_NAME, -s SPREADSHEET_NAME
                        Name of the spreadsheet you want to open.
  --share-with SHARED   [email address] Share the spreadsheet with someone via
                        email
  --update              Update spreadsheet with new prices.
  --loglevel LOG_LEVEL  log level to use, default [INFO], options [INFO,
                        DEBUG, ERROR]
```

Typical usage:

`price_checker.py --json ~/.envs/client_secret.json -s "Shopping List"`

## Oh, Thanks!

By the way... Click if you'd like to [say thanks](https://saythanks.io/to/mmphego)... :) else *Star* it.

✨🍰✨

## Feedback

Feel free to fork it or send me PR to improve it.

