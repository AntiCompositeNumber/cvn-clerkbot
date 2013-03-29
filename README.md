# CVNClerkBot

## Get started

1. Download [CVNClerkBot](https://github.com/countervandalism/CVNClerkBot)

2. Make sure you have the required packages:
   - `twisted` ([Twisted](https://twistedmatrix.com/))
   - `wikilog` ([Krinkle/ts-krinkle-pywiki](https://github.com/Krinkle/ts-krinkle-pywiki/blob/master/wikilog.py))
   - `wikipedia` ([Pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikipediabot))
   - `FurriesBotSQLdb` (only needed if `config.useMySQL=True`)
     - `MySQLdb`

3. Rename `cvnclerkbotconfig-sample.py` to `cvnclerkbotconfig.py` and edit the file as needed.

4. Make sure your `$PYTHONPATH` includes the path to `pywikipedia/` and `ts-krinkle-pywiki/`

5. Navigate to the pywiki directory and execute `$ python cvnclerkbot.py`
