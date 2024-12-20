# Crawling_tfmkt

You'll find in this repository all our codes and results for the Data Acquisition project.

- To run crawling of TransferMrkt, run the script `run_crawl.sh` :

````bash
./run_crawl.sh
````
This will run the crawling for competitions, then clubs using competitions output. And then players using clubs output. The spiders can be found in the folder `tfmkt_scraper/spiders`. The output crawled data is available in the folder `/crawled_data`.

- To run the requests to the Wikipedia API :

````bash
python enrich_players_bios.py
````

- Postprocessing steps can be found in the notebook `postprocessing.ipynb` at the root of the repo.
- The tests we made to choose primary keys for our tables can be found in the notebook `duplicates_and_unique_ids.ipynb`.
- The final database file can be found in the folder `tfmkt_scraper/` along with the python file `table.py` we've used to build our relational tables.
- The file `nodes_rep.py` was created to plot a graph we have used during the presentation.

Students :

Noâm BOUSSOUF

Efstathios CHATZILOIZOS

Emmarius DELAR

