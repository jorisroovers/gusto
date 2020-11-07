# gusto
Meal Planning tool (for personal use). Quick-and-dirty :-)

'Gusto' is a word play on [Gusteau](https://pixar.fandom.com/wiki/Auguste_Gusteau), the legendary chef from Pixar's Ratatouille movie.


# Usage

```sh
# Install dependencies using poetry
poetry install

# Configure
export GUSTO_RECIPES="myrecipes.csv"

# Run cli
python gusto/cli.py -r $GUSTO_RECIPES -w 1

# run webapp
uvicorn --reload --log-config logconfig.ini  gusto.web:app

# Don't auto-reload on changes
uvicorn --log-config logconfig.ini  gusto.web:app
```

# TODO
[ ] Export to CSV
[ ] Serve from docker containers
[ ] Store in DB ()
[ ] Go forth/back a week
[ ] Show contraints names in table
[ ] Highlight today