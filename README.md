Setup:

Create and activate a virtual environment with Python2.7

Run "pip install -r requirements.txt" (Don't forget psycopg2-binaries)

Set up the Postgres database and restore the contents from a backup.

Comment out line 105 in metashare/xml_utils.py, do the XML import ([MetaShare documetation](https://github.com/metashare/META-SHARE/blob/master/misc/docs/META-SHARE_Installation_Manual.rst#importing-from-the-command-line)), and re-add the line.

Copy local_settings.py to metashare/ (may need to change the logfile path therein).

cd metashare/

Run "./start_solr.sh"

Run "python ../manage.py runserver"
