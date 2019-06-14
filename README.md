# Shopping List Bot

[![Build Status](https://travis-ci.com/mmphego/shopping_list_bot.svg?branch=master)](https://travis-ci.com/mmphego/shopping_list_bot)
![GitHub](https://img.shields.io/github/license/mmphego/shopping_list_bot.svg)

## {{ STORY GOES HERE}}


## Installation

Before you install ensure that `geckodrive` for Firefox is installed.

*   Download [geckodriver](https://github.com/mozilla/geckodriver)
    -   ```wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz```
    -   Extract: ```tar -xvzf geckodriver-v0.24.0-linux64.tar.gz```
*   Copy `geckodriver` to /usr/local/bin

Now install:
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

