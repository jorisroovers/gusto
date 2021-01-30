# gusto
Meal Planning tool (for personal use). **Quick-and-dirty :-)**

'Gusto' is a word play on [Gusteau](https://pixar.fandom.com/wiki/Auguste_Gusteau), the legendary chef from Pixar's Ratatouille movie.


# Usage

```sh
# Install dependencies using poetry
poetry install

poetry shell

# Run cli
python gusto/gusto/cli.py -r $GUSTO_RECIPES -w 1

# run webapp
uvicorn --reload --log-config config/logconfig.ini --app-dir gusto --env-file config/config-local.env gusto.web:app
```

#  Docker
```sh
docker build -t gusto:latest .
docker run --rm -d --name gusto -p 8000:80 --env-file config/config-docker.env  -v $(pwd)/config:/config -v $(pwd)/gusto.db:/data/gusto.db gusto
```

# Alembic
[Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html) is used for Database management and migrations

```sh
# To initially setup alembic
alembic init alembic

# Run migrations
alembic upgrade head
```


# TODO
- [x] Host Gusto on casa!
- [ ] Recipe Selection search based on constraint
- [ ] Constraint list export
- [ ] Export to CSV
- [x] Serve from docker containers
- [x] Store in DB
- [ ] Go forth/back a week
- [x] Show constraints names in table
- [ ] Add pictures based on slack monitoring
- [ ] Highlight today
- [ ] Toggle Edit button
- [ ] Docker DEBUG logs
- [ ] Notification System
- [x] Recipe Search/filter
