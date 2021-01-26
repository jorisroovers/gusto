import logging
import os

import arrow
from starlette.applications import Starlette
from starlette.config import Config
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .mealplan import MealPlan, MealPlanGenerator, Importer
from .controllers import GustoController

from . import models

import sqlalchemy
from sqlalchemy.orm import sessionmaker

LOG = logging.getLogger("gusto.web")

### CONFIG #############################################################################################################

config = Config(".env")
RECIPES_CSV = config('GUSTO_RECIPES')
DATABASE_URL = config('GUSTO_DATABASE_URL')

base_path = os.path.dirname(__file__)
static_dir = os.path.join(base_path, "../static")
template_dir = os.path.join(base_path, "../templates")

templates = Jinja2Templates(directory=template_dir)
templates.env.variable_start_string = "[["
templates.env.variable_end_string = "]]"

### REQUESTS ###########################################################################################################

async def homepage(request):
    return templates.TemplateResponse('mealplan.html', {'request': request})

async def recipes(request):
    return templates.TemplateResponse('recipes.html', {'request': request})

### API ################################################################################################################


async def regen_mealplan(request):
    data = await request.json()
    start_date = arrow.get(data['start_date'])
    request.app.state.mealplan = request.app.state.mealplan_generator.generate_mealplan(start_date, 1)
    return JSONResponse({'status': "success"})

async def regen_meal(request):
    data = await request.json()
    meal_index = int(data['meal_index'])
    meal = request.app.state.mealplan.meals[meal_index]
    new_meal = request.app.state.mealplan_generator.regenerate_meal(meal)
    request.app.state.mealplan.meals[meal_index] = new_meal

    LOG.debug("Regenerated Mealplan %s", request.app.state.mealplan)
    return JSONResponse({'status': "success"})

async def api_meals(request):
    controller = GustoController(request, models.Meal)
    filters = []
    if 'after' in request.query_params:
        filters.append(models.Meal.date >= request.query_params['after'])
    if 'before' in request.query_params:
        filters.append(models.Meal.date < request.query_params['before'])
    return JSONResponse({'meals': controller.filter(*filters) })

async def mealplan(request):
    return JSONResponse({'mealplan': request.app.state.mealplan.for_json()})

async def api_recipes(request):
    controller = GustoController(request, models.Recipe)
    return JSONResponse({'recipes': controller.list()})

async def api_export(request):
    request.app.state.mealplan.export_to_csv("export.csv")
    return JSONResponse({'recipes': request.app.state.recipes.recipes})

### STARTUP #############################################################################################################

async def startup():
    engine = sqlalchemy.create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    app.state.db_session = Session()
    models.startup(app.state.db_session)

    importer = Importer(app.state.db_session)
    importer.import_from_csv(os.path.realpath(RECIPES_CSV))

    # app.state.mealplan_generator = MealPlanGenerator(recipes_controller.list())
    # Next Monday
    start_date  = arrow.utcnow().shift(weekday=0)
    # This week's Monday
    # start_date  = arrow.utcnow().shift(weeks=-1, weekday=0)
    app.state.mealplan =  None # app.state.mealplan_generator.generate_mealplan(start_date, 1)

def shutdown():
    LOG.debug("Shutting Down")
    app.state.db_session.close()
    LOG.debug("Shudown complete. bye 👋")

app = Starlette(debug=True, on_startup=[startup], on_shutdown=[shutdown], routes=[
    Route('/', homepage),
    Route('/recipes', recipes),
    Mount('/static', StaticFiles(directory=static_dir), name='static'),
    Route('/api/meals', api_meals),
    Route('/api/mealplan', mealplan),
    Route('/api/recipes', api_recipes),
    Route('/api/regen_meal', regen_meal, methods=['POST']),
    Route('/api/regen_mealplan', regen_mealplan, methods=['POST']),
    Route('/api/export', api_export, methods=['POST']),
])
