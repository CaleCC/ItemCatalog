# ItemCatalog
An item catalog application

## Runtime environment Requirements
* Python3 Interpreter
* An up-and-running PostgreSQL empty database named "news"
* psycopg2 library

You can setup the environment using VirtualBox/Vagrant tool.
Download the Vagrant file from [here](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f73b_vagrantfile/vagrantfile).


## To begin
* Clone this repository to your vangrant directory.
* Start vagrant by `vagrant up` and `vagrant ssh`
* Modify line 29 in login.html with your own google oauth client ID
* Download the Json file of your oauth application from Google Developer Console and rename it as `client_secrets.json`
* In the directory of this project, run `python insertSomeData.py` to create the database and insertsome sampe item data.
* Start the server  `python itemcatalog.py`
* Access the site http://locaslhost:8000
*  The end point that returns an json of an item is http://locaslhost:8000//item/<int:item_id>/json

