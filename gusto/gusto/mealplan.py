from os import name
import csv
import uuid
import copy
import logging
import random

from rich.console import Console

LOG = logging.getLogger("gusto.mealplan")
console = Console()

class Recipes:
    def __init__(self) -> None:
        self.recipes = []

    def import_from_csv(self, filename) -> None:
        LOG.debug("Reading from %s", filename)
        recipes = {}
        with open(filename) as csv_file:
            records = csv.DictReader(csv_file)
            record_count = 0
            for record in records:
                record_count+=1
                record['parsed-tags'] = [l.strip() for l in record['Tags'].split(",") if l.strip() != ""]
                recipes[record['Name']] = record

            LOG.info(f"Read {record_count} recipes ({len(recipes)} unique) from {filename}")

        self.recipes.extend(recipes.values())


class Constraint:
    def __init__(self, title: str, match_func = None) -> None:
        self.id = str(uuid.uuid4())
        self.title = title
        self.match_func = match_func

    def match(self, recipe: dict) -> bool:
        if self.match_func:
            return self.match_func(recipe)
        return False

    def for_json(self) -> dict:
        return {"id": self.id, "title": self.title}


class TagConstraint(Constraint):

    def __init__(self, title , included_tags, excluded_tags) -> None:
        super().__init__(title)
        self.included_tags = included_tags
        self.excluded_tags = excluded_tags

    def match(self, recipe: dict) -> bool:
        return all(tag in recipe['parsed-tags'] for tag in self.included_tags) and \
               all(tag not in recipe['parsed-tags'] for tag in self.excluded_tags )


MEAL_CONSTRAINTS = [ TagConstraint("Veggie Dag", ["Vegetarisch"], ["Zondigen", "Overschot", "Exclude"]), 
                     TagConstraint("Vis Dag", ["Vis"], ["Zondigen", "Overschot", "Exclude"]), 
                     TagConstraint("Asian Dag", ["Asian"], ["Zondigen", "Overschot", "Exclude"]),
                     TagConstraint("Steak Dag", ["Steak"], ["Zondigen", "Overschot", "Exclude"]),
                     TagConstraint("Pasta Dag", ["Pasta"], ["Zondigen", "Overschot", "Exclude"]),
                     TagConstraint("Vrije Dag", [], ["Zondigen", "Overschot", "Exclude"])
                    ]

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

class MealPlanGenerator:

    def __init__(self, recipes) -> None:
        self.recipe_pool = { r['Name']: r  for r in recipes.recipes}

    def generate_mealplan(self, start_date, num_weeks: int) -> MealPlan:
        meals = []
        day_offset = 0
        for _ in range(num_weeks):
            # Add some randomness to when we eat what, but ensure Friday is "Zondigen"
            day_constraints = copy.copy(MEAL_CONSTRAINTS)
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
