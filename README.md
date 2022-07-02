# winestock

A tool to help find good wines at a specific store by querying [Vivino](https://www.vivino.com). The end result is a CSV file that details information for each wine including Vivino rating.

The tool currently works for:
- [Berkeley Bowl West](https://shop.heinzcatering.berkeleybowl.com/department/beer_wine)
- [Wine.com](https://www.wine.com/)

It works by fetching a page of wines from the shop, then searching for individual wines on Vivino to provide ratings. A second search round requests information from the specific wine URLs collected in the first round, including price, regions, and specific information for the vintage if provided.

### Note on using Vivino ratings

Vivino ratings (out of 5) are **not** an objective source of wine quality. I have personally found wines above a rating of 4 that I thought weren't great quality. I have gad great wines at 3.8. However I've found that quality quickly drops off under 3.8.

My general approach is to not consider wines under 3.8, but past that select for other things like price, discount, or just fun varieties.

# How to

Set up the python environment with

    conda env create -f environment.yml

Open the ```scraper.ipynb``` notebook in the ```winestock``` environment and follow the instructions.
