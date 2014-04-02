# CVNClerkBot [![Build Status](https://travis-ci.org/countervandalism/CVNClerkBot.svg?branch=master)](https://travis-ci.org/countervandalism/CVNClerkBot)

## Get started

1. Download [CVNClerkBot](https://github.com/countervandalism/CVNClerkBot)

2. Make sure you have the required packages:
   - `twisted` ([Twisted](https://twistedmatrix.com/))
   - `wikipedia` ([Pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikipediabot))
   - `FurriesBotSQLdb` (only needed if `config.useMySQL=True`)
     - `MySQLdb`

3. Rename `cvnclerkbotconfig-sample.py` to `cvnclerkbotconfig.py` and edit the file as needed.

4. Make sure your `$PYTHONPATH` includes the path to `pywikipedia/`.

5. Navigate to the pywiki directory and execute `$ python cvnclerkbot.py`.
