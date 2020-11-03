# gusto
Meal Planning tool (for personal use). Quick-and-dirty :-)

'Gusto' is a word play on [Gusteau](https://pixar.fandom.com/wiki/Auguste_Gusteau), the legendary chef from Pixar's Ratatouille movie.


# Usage

```sh
# Install dependencies using poetry
poetry install

# Run cli
python gusto/cli.py -r myrecipes.csv -w 1

# run webapp
uvicorn gusto.web:app
```