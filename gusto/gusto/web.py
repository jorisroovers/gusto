import logging
import os

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.config import Config
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from .mealplan import MealPlan, Recipes

LOG = logging.getLogger("gusto.web")

### CONFIG #############################################################################################################

config = Config(".env")
RECIPES_CSV = config('GUSTO_RECIPES')

templates = Jinja2Templates(directory='templates')
templates.env.variable_start_string = "[["
templates.env.variable_end_string = "]]"

### REQUESTS ###########################################################################################################

async def homepage(request):
    return templates.TemplateResponse('mealplan.html', {'request': request})

async def recipes(request):
    return templates.TemplateResponse('recipes.html', {'request': request})

### API ################################################################################################################

async def regen(request):
    data = await request.json()
    if data['meal_index'] == "all":
        request.app.state.mealplan.generate_mealplan(1)
    else:
        request.app.state.mealplan.regenerate_meal(int(data['meal_index']))

    LOG.debug("Regenerated Mealplan %s", request.app.state.mealplan.mealplan)
    return JSONResponse({'status': "success"})

async def mealplan(request):
    mealplan = request.app.state.mealplan.mealplan
    return_list = []
    for meal in mealplan:
        return_list.append(meal.for_json())

    LOG.debug("Mealplan %s", mealplan)

    return JSONResponse({'mealplan': return_list})

async def api_recipes(request):
    return JSONResponse({'recipes': request.app.state.recipes.recipes})

async def api_export(request):
    request.app.state.mealplan.export_to_csv("export.csv")
    return JSONResponse({'recipes': request.app.state.recipes.recipes})

### STARTUP #############################################################################################################

def startup():
    recipes = Recipes()
    recipes.import_from_csv(os.path.realpath(RECIPES_CSV))
    mealplan = MealPlan(recipes=recipes)
    mealplan.generate_mealplan(1)
    app.state.recipes = recipes
    app.state.mealplan = mealplan

app = Starlette(debug=True, on_startup=[startup], routes=[
    Route('/', homepage),
    Route('/recipes', recipes),
    Mount('/static', StaticFiles(directory='static'), name='static'),
    Route('/api/mealplan', mealplan),
    Route('/api/recipes', api_recipes),
    Route('/api/regen', regen, methods=['POST']),
    Route('/api/export', api_export, methods=['POST']),
])

