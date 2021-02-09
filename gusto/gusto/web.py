import asyncio
import logging
import os

import arrow
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from starlette.applications import Starlette
from starlette.config import Config
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket
from starlette.endpoints import HTTPEndpoint


from . import models
from .controllers import GustoController
from .mealplan import Importer, MealPlan, MealPlanGenerator

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

### PAGES ##############################################################################################################

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

class Meals(HTTPEndpoint):
    async def get(self, request):
        controller = GustoController(request, models.Meal)
        filters = []
        if 'after' in request.query_params:
            filters.append(models.Meal.date >= request.query_params['after'])
        if 'before' in request.query_params:
            filters.append(models.Meal.date < request.query_params['before'])
        return JSONResponse({'meals': controller.filter(*filters) })

    async def post(self, request):
        data = await request.json()
        controller = GustoController(request, models.Meal)
        LOG.debug("Adding meal %s", data)
        controller.create(models.Meal(date=arrow.get(data['meal']['date']).date(), recipe_id=data['meal']['recipe_id']))
        LOG.debug("Creating meal")
        return JSONResponse({'status': "success"})

class Meal(HTTPEndpoint):

    async def delete(self, request):
        meal_id = request.path_params['meal_id']
        LOG.debug("Deleting meal %d", meal_id)
        controller = GustoController(request, models.Meal)
        controller.delete(models.Meal.id == meal_id)
        return JSONResponse({'status': "success"})

async def mealplan(request):
    return JSONResponse({'mealplan': request.app.state.mealplan.for_json()})

async def api_export(request):
    request.app.state.mealplan.export_to_csv("export.csv")
    return JSONResponse({'recipes': request.app.state.recipes.recipes})

async def api_navigate(request):
    data = await request.json()
    LOG.debug("Sending message to websockets to navigate to %s", data['url'])
    for ws in request.app.state.websockets:
        try:
            await ws.send_json({"url": data['url']})
        except Exception:
            LOG.debug("Error during api navigate")
            pass

    return JSONResponse({"status": "success"})

class Recipes(HTTPEndpoint):
    async def get(self, request):
        controller = GustoController(request, models.Recipe)
        return JSONResponse({'recipes': controller.list()})

    async def post(self, request):
        data = await request.json()
        controller = GustoController(request, models.Recipe)
        LOG.debug("Adding recipe %s", data)
        controller.create(models.Recipe(**data))
        return JSONResponse({'status': "success"})

class Recipe(HTTPEndpoint):

    async def delete(self, request):
        recipe_id = request.path_params['recipe_id']
        LOG.debug("Deleting recipe %d", recipe_id)
        controller = GustoController(request, models.Recipe)
        controller.delete(models.Recipe.id == recipe_id)
        return JSONResponse({'status': "success"})


### Websockets #########################################################################################################

async def ws_navigation(websocket: WebSocket):
    await websocket.accept()
    websocket.app.state.websockets.append(websocket)

    try:
        while True:
            LOG.debug("Websocket nav, websockets: %d", len(websocket.app.state.websockets))
            msg = await asyncio.wait_for(websocket.receive(), timeout=3600.0)
    except (asyncio.exceptions.TimeoutError):
        pass
    finally:
        LOG.debug("Websocket nav, running finally")
        # Always remove sockets, independent of what exception occurred
        websocket.app.state.websockets.remove(websocket)
        await websocket.close()
        LOG.debug("after finally, websockets: %d", len(websocket.app.state.websockets))


### STARTUP ############################################################################################################


async def startup():
    engine = sqlalchemy.create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    app.state.db_session = Session()
    app.state.websockets = []
    models.startup(app.state.db_session)

    import_file = os.path.realpath(RECIPES_CSV)
    if os.path.exists(import_file):
        importer = Importer(app.state.db_session)
        importer.import_from_csv(import_file)

    # app.state.mealplan_generator = MealPlanGenerator(recipes_controller.list())
    # Next Monday
    start_date  = arrow.utcnow().shift(weekday=0)
    # This week's Monday
    # start_date  = arrow.utcnow().shift(weeks=-1, weekday=0)
    app.state.mealplan =  None # app.state.mealplan_generator.generate_mealplan(start_date, 1)

def shutdown():
    LOG.debug("Shutting Down")
    app.state.db_session.close()
    LOG.debug("Shutdown complete. bye 👋")

app = Starlette(debug=True, on_startup=[startup], on_shutdown=[shutdown], routes=[
    Mount('/static', StaticFiles(directory=static_dir), name='static'),
    Route('/', homepage),
    Route('/recipes', recipes),
    WebSocketRoute('/ws/navigation', ws_navigation),
    Mount('/api', routes=[
        Route('/meals', Meals),
        Route('/meal/{meal_id:int}', Meal),
        Route('/mealplan', mealplan),
        Route('/recipes', Recipes),
        Route('/recipes/{recipe_id:int}', Recipe),
        Route('/regen_meal', regen_meal, methods=['POST']),
        Route('/regen_mealplan', regen_mealplan, methods=['POST']),
        Route('/export', api_export, methods=['POST']),
        Route('/navigate', api_navigate, methods=['POST']),
    ]),
])
