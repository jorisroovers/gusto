import copy
import csv
import logging
import random
import uuid
from os import name

import arrow
from rich.console import Console

LOG = logging.getLogger("gusto.mealplan")
console = Console()

from . import models
from .controllers import GustoController

from .constraints import Constraint, TagConstraint, CONSTRAINTS

class Importer:
    def __init__(self, db_session) -> None:
        self.db = db_session

    def import_from_csv(self, filename) -> None:
        LOG.debug("Reading from %s", filename)
        recipes = {}
        existing_recipes = dict({(recipe.name, recipe) for recipe in self.db.query(models.Recipe).all()})
        with open(filename) as csv_file:
            records = csv.DictReader(csv_file)
            record_count = 0
            for record in records:
                record_count+=1
                record['parsed-tags'] = [l.strip() for l in record['Tags'].split(",") if l.strip() != ""]
                recipes[record['Name']] = record

                # TODO: continue here:
                # - remove return value. We should just do another list() operation to get all recipes/meals

                recipe  = existing_recipes.get(record['Name'], False)

                if not recipe:
                    recipe = models.Recipe(name=record['Name'], description="", comments=record['Comments'],
                            url=record['URL'], tags=",".join(record['parsed-tags']))
                    self.db.add(recipe)
                    existing_recipes[recipe.name] = recipe
                    self.db.commit()
                
                if record['Date'] != '':
                    mealplan_date = arrow.get(record['Date'], "MMM D, YYYY").date()
                    existing_meal = self.db.query(models.Meal).filter(models.Meal.date==mealplan_date).first()
                    
                    # If there's already a meal in the database for the date,
                    # don't overwrite (this would error out anyways because of unique constraint)
                    if not existing_meal:
                        meal = models.Meal(recipe_id=recipe.id, date=mealplan_date)
                        self.db.add(meal)
                        self.db.commit()


            LOG.info(f"Read {record_count} recipes ({len(recipes)} unique) from {filename}")
        self.db.commit()

class Meal:

    def __init__(self, recipe: dict, date, constraint) -> None:
        self.recipe = recipe
        self.date = date
        self.constraint = constraint

    def for_json(self) -> dict:
        return {"recipe": self.recipe, "date": self.date.for_json(), "constraint": self.constraint.for_json() }

    def __str__(self) -> str:
        return self.recipe

class MealPlan:

    def __init__(self) -> None:
        self.meals = []

    
    def for_json(self) -> dict:
        return {"meals": [meal.for_json() for meal in self.meals] }


    def export_to_csv(self, filename: str):
        LOG.info(f"Exporting to [yellow]{filename}[/]")

        with open(filename, 'w') as export_file:
            fieldnames = ["Done", "Weekd", "Date", "Name", "Tags", "Comments", "URL", "Score"]
            exporter = csv.DictWriter(export_file, fieldnames=fieldnames, extrasaction="ignore")
            exporter.writeheader()
            for meal in self.meals:
                meal.recipe.update({
                    'Date': meal.date.format('MMM D, YYYY'),
                    'Done':"No",
                    'Weekd': ""
                })
                exporter.writerow(meal.recipe)



WEEK_CONSTRAINTS = [
    CONSTRAINTS['veggie-day'], CONSTRAINTS['fish-day'], CONSTRAINTS['asian-day'], CONSTRAINTS['steak-day'], CONSTRAINTS['pasta-day'], CONSTRAINTS['free-day'],
]
class MealPlanGenerator:

    def __init__(self, recipes) -> None:
        self.recipe_pool = { r['Name']: r  for r in recipes.recipes}

    def generate_mealplan(self, start_date, num_weeks: int) -> MealPlan:
        meals = []
        day_offset = 0
        for _ in range(num_weeks):
            # Add some randomness to when we eat what, but ensure Friday is "Zondigen"
            day_constraints = copy.copy(WEEK_CONSTRAINTS)
            random.shuffle(day_constraints)
            day_constraints.insert(4, Constraint("Vettige Vrijdag", lambda r: "Zondigen" in r['parsed-tags']))
            
            for constraint in day_constraints:
                recipe = random.choice(self.generate_recipe_set(constraint))
                meal = Meal(recipe, start_date.shift(days=day_offset), constraint)
                self.recipe_pool.pop(meal.recipe['Name'])
                meals.append(meal)
                day_offset += 1

        mealplan = MealPlan()
        mealplan.meals = meals
        return mealplan

    def generate_recipe_set(self, constraint: Constraint) -> list:
        return [ r for r in self.recipe_pool.values() if constraint.match(r) ]

    def regenerate_meal(self, meal) -> Meal:
        recipe = random.choice([ r for r in self.recipe_pool.values() if meal.constraint.match(r) ])
        # Add original meal recipe back to to the pool, so we can use it again
        self.recipe_pool[recipe['Name']] = recipe
        meal.recipe = recipe
        return meal
