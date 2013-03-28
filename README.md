## Install

1. Get the latest source from https://github.com/countervandalism/CVNClerkBot

2. Make sure you have the required packages:
   - `python-twisted` (used by `cvnclerkbot.py`)
   - `wikilog` (used by `cvnclerkbot.py`)
     Source: https://github.com/Krinkle/ts-krinkle-pywiki/blob/master/wikilog.py
     - `pywikipedia` (used by `wikilog.py`)
       Source: https://www.mediawiki.org/wiki/Manual:Pywikipediabot
   - `FurriesBotSQLdb.py` (optional, only if `config.useMySQL` is True)
     - `MySQLdb` (used by `FurriesBotSQLdb.py`)

3. Rename `cvnclerkbotconfig-sample.py` to `cvnclerkbotconfig.py` and edit the file as needed.

4. Set up symlinks inside the `./pywikipedia` checkout pointing to these files:
   - `cvnclerkbot.py`
   - `cvnclerkbotconfig.py`
   - `FurriesBotSQLdb.py`
   - `wikilog.py`

   For example:
   `pywikipedia$ ln -s $HOME/externals/p_cvn/trunk/CVN-ClerkBot/cvnclerkbot.py cvnclerkbot.py`

5. Navigate to the pywiki directory and execute:
   `$ python cvnclerkbot.py`
