import arrow
import logging
import os

import databases
import sqlalchemy

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.config import Config
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from .mealplan import MealPlan, MealPlanGenerator, Recipes

LOG = logging.getLogger("gusto.web")

### CONFIG #############################################################################################################

config = Config(".env")
RECIPES_CSV = config('GUSTO_RECIPES')
DATABASE_URL = config('DATABASE_URL')

templates = Jinja2Templates(directory='templates')
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

async def mealplan(request):
    return JSONResponse({'mealplan': request.app.state.mealplan.for_json()})

async def api_recipes(request):
    return JSONResponse({'recipes': request.app.state.recipes.recipes})

async def api_export(request):
    request.app.state.mealplan.export_to_csv("export.csv")
    return JSONResponse({'recipes': request.app.state.recipes.recipes})

### STARTUP #############################################################################################################

async def startup():
    recipes = Recipes()
    await recipes.import_new2()
    recipes.import_from_csv(os.path.realpath(RECIPES_CSV))
    app.state.recipes = recipes
    app.state.mealplan_generator = MealPlanGenerator(app.state.recipes)
    # Next Monday
    start_date  = arrow.utcnow().shift(weekday=0)
    # This week's Monday
    # start_date  = arrow.utcnow().shift(weeks=-1, weekday=0)
    app.state.mealplan =  None # app.state.mealplan_generator.generate_mealplan(start_date, 1)

def shutdown():
    LOG.debug("Shutting Down")


app = Starlette(debug=True, on_startup=[startup], on_shutdown=[shutdown], routes=[
    Route('/', homepage),
    Route('/recipes', recipes),
    Mount('/static', StaticFiles(directory='static'), name='static'),
    Route('/api/mealplan', mealplan),
    Route('/api/recipes', api_recipes),
    Route('/api/regen_meal', regen_meal, methods=['POST']),
    Route('/api/regen_mealplan', regen_mealplan, methods=['POST']),
    Route('/api/export', api_export, methods=['POST']),
])

