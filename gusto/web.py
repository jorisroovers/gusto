import os
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.config import Config

from .mealplan import MealPlan, Recipes

### CONFIG #############################################################################################################

config = Config(".env")
RECIPES_CSV = config('GUSTO_RECIPES')


### REQUESTS ###########################################################################################################


async def homepage(request):
    # TODO: fix serialization of mealplan, use arrow.utcnow().for_json() maybe?
    mealplan = request.app.state.mealplan.mealplan
    return JSONResponse({'hello': mealplan[0]['Name']})


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
])

