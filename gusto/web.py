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


### REQUESTS ###########################################################################################################

async def homepage(request):
    return templates.TemplateResponse('index.html', {'request': request})

async def regen(request):
    request.app.state.mealplan.generate_mealplan(app.state.recipes, 1)
    LOG.debug("Regenerated Mealplan %s", request.app.state.mealplan.mealplan)
    return JSONResponse({'status': "success"})

async def mealplan(request):
    # TODO: fix serialization of mealplan, use arrow.utcnow().for_json() maybe?
    mealplan = request.app.state.mealplan.mealplan
    LOG.debug("Mealplan %s", mealplan)

    return JSONResponse({'mealplan': mealplan[0]['Name']})

### STARTUP #############################################################################################################

def startup():
    recipes = Recipes()
    recipes.import_from_csv(os.path.realpath(RECIPES_CSV))
    mealplan = MealPlan()
    mealplan.generate_mealplan(recipes, 1)
    app.state.recipes = recipes
    app.state.mealplan = mealplan

app = Starlette(debug=True, on_startup=[startup], routes=[
    Route('/', homepage),
    Route('/mealplan', mealplan),
    Route('/regen', regen),
    Mount('/static', StaticFiles(directory='static'), name='static')
])

