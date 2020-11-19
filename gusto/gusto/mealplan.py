from os import name
import arrow
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


MEAL_CONSTRAINTS = [ TagConstraint("Veggie Dag", ["Vegetarisch"], ["Zondigen"]), 
                     TagConstraint("Vis Dag", ["Vis"], ["Zondigen"]), 
                     TagConstraint("Asian Dag", ["Asian"], ["Zondigen"]),
                     TagConstraint("Steak Dag", ["Steak"], ["Zondigen"]),
                     TagConstraint("Pasta Dag", ["Pasta"], ["Zondigen"]),
                     TagConstraint("Vrije Dag", [], ["Zondigen"])
                    ]

class Meal:

    def __init__(self, recipe: dict, date, constraint) -> None:
        self.recipe = recipe
        self.date = date
        self.constraint = constraint

    def for_json(self) -> dict:
        return {"recipe": self.recipe, "date": self.date.for_json(), "constraint": self.constraint.for_json() }


class MealPlan:

    def __init__(self, recipes) -> None:
        self.mealplan = []
        self.recipe_pool = { r['Name']: r  for r in recipes.recipes}

    def generate_mealplan(self, num_weeks: int) -> None:
        # Compose mealplan
        mealplan = []
        
        # Next Monday
        # start_date  = arrow.utcnow().shift(weekday=0)
        # This week's Monday
        start_date  = arrow.utcnow().shift(weeks=-1, weekday=0)
        
        
        day_offset = 0
        for _ in range(num_weeks):
            # Add some randomness to when we eat what, but ensure Friday is "Zondigen"
            day_constraints = copy.copy(MEAL_CONSTRAINTS)
            random.shuffle(day_constraints)
            day_constraints.insert(4, Constraint("Vettige Vrijdag", lambda r: "Zondigen" in r['parsed-tags']))
            
            for constraint in day_constraints:
                recipe = random.choice([ r for r in self.recipe_pool.values() if constraint.match(r) ])
                meal = Meal(recipe, start_date.shift(days=day_offset), constraint)
                self.recipe_pool.pop(meal.recipe['Name'])
                mealplan.append(meal)
                day_offset += 1

        self.mealplan = mealplan


    def regenerate_meal(self, meal_index: int) -> None:
        meal = self.mealplan[meal_index]
        recipe = random.choice([ r for r in self.recipe_pool.values() if meal.constraint.match(r) ])
        # Add original meal recipe back to to the pool, so we can use it again
        self.recipe_pool[recipe['Name']] = recipe
        meal.recipe = recipe

    def export_to_csv(self, filename: str):
        LOG.info(f"Exporting to [yellow]{filename}[/]")

        with open(filename, 'w') as export_file:
            fieldnames = ["Done", "Weekd", "Date", "Name", "Tags", "Comments", "URL", "Score"]
            exporter = csv.DictWriter(export_file, fieldnames=fieldnames, extrasaction="ignore")
            exporter.writeheader()
            for meal in self.mealplan:
                meal.recipe.update({
                    'Date': meal.date.format('MMM D, YYYY'),
                    'Done':"No",
                    'Weekd': ""
                })
                exporter.writerow(meal.recipe)
