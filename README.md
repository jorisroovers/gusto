# gusto
Meal Planning tool (for personal use). Quick-and-dirty :-)

'Gusto' is a word play on [Gusteau](https://pixar.fandom.com/wiki/Auguste_Gusteau), the legendary chef from Pixar's Ratatouille movie.


# Usage

```sh
# Install dependencies using poetry
poetry install

poetry shell

cd gusto

# Configure
export GUSTO_RECIPES="../config/Meal-Planning.csv"

# Run cli
python gusto/gusto/cli.py -r $GUSTO_RECIPES -w 1

# run webapp
uvicorn --reload --log-config ../config/logconfig.ini gusto.web:app
```

#  Docker
```sh
docker build -t gusto:latest .
docker run -d --name gusto -p 8000:80 --env-file config/config.env  -v $(pwd)/config:/config  gusto
```

# TODO
- [ ] Export to CSV
- [ ] Serve from docker containers
- [ ] Store in DB ()
- [ ] Go forth/back a week
- [x] Show constraints names in table
- [ ] Highlight today
- [ ] Toggle Edit button
- [ ] Notification System