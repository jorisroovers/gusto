from os import name
import arrow
import csv
import copy
import json
import logging
import random

from rich.console import Console

LOG = logging.getLogger("gusto.mealplan")
console = Console()

class Recipes:
    def __init__(self) -> None:
        self.recipes = {}

    def import_from_csv(self, filename) -> None:
        LOG.debug("Reading from %s", filename)
        recipes = {}
        with open(filename) as csv_file:
            records = csv.DictReader(csv_file)
            record_count = 0
            for record in records:
                record_count+=1
                record['parsed-labels'] = [l.strip() for l in record['Labels'].split(",")]
                recipes[record['Name']] = record

            LOG.info(f"Read {record_count} recipes ({len(recipes)} unique) from {filename}")

        self.recipes.update(recipes)


class Meal:

    def __init__(self, recipe: dict, date, constraint) -> None:
        self.recipe = recipe
        self.date = date
        self.constraint = constraint

    def for_json(self):
        return {"recipe": self.recipe, "date": self.date.for_json() }



class MealPlan:

    def __init__(self) -> None:
        self.mealplan = []

    def generate_mealplan(self, recipes: Recipes, num_weeks: int) -> None:
        # Compose mealplan
        recipe_list = copy.deepcopy(recipes.recipes)
        mealplan = []
        start_date  = arrow.utcnow().shift(weekday=0)
        day_offset = 0
        for _ in range(num_weeks):
            # Add some randomness to when we eat what, but ensure Friday is "Zondigen"
            day_constraints = [lambda r: "Vegetarisch" in r['parsed-labels'] and "Zondigen" not in r['parsed-labels'],
                            lambda r: "Vis" in r['parsed-labels'] and "Zondigen" not in r['parsed-labels'],
                            lambda r: "Asian" in r['parsed-labels']  and "Zondigen" not in r['parsed-labels'],
                            lambda r: "Steak" in r['parsed-labels']  and "Zondigen" not in r['parsed-labels'],
                            lambda r: "Pasta" in r['parsed-labels']  and "Zondigen" not in r['parsed-labels'],
                            lambda r: "Zondigen" not in r['parsed-labels']
                            ]
            random.shuffle(day_constraints)
            day_constraints.insert(4, lambda r: "Zondigen" in r['parsed-labels'])
            
            for constraint in day_constraints:
                recipe = random.choice([ r for r in recipe_list.values() if constraint(r) ])
                meal = Meal(recipe, start_date.shift(days=day_offset), constraint)
                recipe_list.pop(meal.recipe['Name'])
                mealplan.append(meal)
                day_offset += 1

        self.mealplan = mealplan


    def export_to_csv(self, filename: str):
        LOG.info(f"Exporting to [yellow]{filename}[/]")

        with open(filename, 'w') as export_file:
            fieldnames = ["Gedaan", "Weekd", "Datum", "Name", "Labels", "Comments", "URL", "Score", "Weekdag" ]
            exporter = csv.DictWriter(export_file, fieldnames=fieldnames, extrasaction="ignore")
            exporter.writeheader()
            for meal in self.mealplan:
                meal.recipe.update({
                    'Datum': meal.date.format('MMM D, YYYY'),
                    'Gedaan':"No",
                    'Weekdag': "",
                    'Weekd': ""
                })
                exporter.writerow(meal.recipe)
