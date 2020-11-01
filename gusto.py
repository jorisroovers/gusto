
import csv
import random
import re

import arrow
import click
from rich.console import Console
from rich.table import Table


def print_mealplan(mealplan):
    """ Pretty prints a menu to the console """
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Weekday", style="dim", width=12)
    table.add_column("Date", style="dim")
    table.add_column("Recipe")
    table.add_column("Labels", justify="right")

    for i, menu in enumerate(mealplan):
        # labels_str = choice['Labels'].replace(choice['match'], f"[b][u]{choice['match']}[/][/]")
        table.add_row(menu['date'].format('dddd'), menu['date'].format('YYYY-MM-DD'), 
                      menu['Name'], menu['Labels'])
        
        # Add empty row after each week
        if ((menu['date'].format('dddd') == "Sunday") and (i != len(mealplan)-1)):
            table.add_row()

    console.print(table)


def export_mealplan(mealplan):
    console = Console()

   
    timestamp = arrow.now().format('YYYY-MM-DD_HH-mm-ss')
    export_filename = f"gusto-export-{timestamp}.csv"
    console.print(f"Exporting to [yellow]{export_filename}[/]")

    with open(export_filename, 'w') as export_file:
        fieldnames = ["Gedaan", "Weekd", "Datum", "Name", "Labels", "Comments", "URL", "Score", "Weekdag" ]
        exporter = csv.DictWriter(export_file, fieldnames=fieldnames, extrasaction="ignore")
        exporter.writeheader()
        exporter.writerows(mealplan)

def import_recipes(filename):
    console = Console()

    # Parse CSV
    recipes = {}
    records = csv.DictReader(filename)
    record_count = 0
    for record in records:
        record_count+=1
        record['parsed-labels'] = [l.strip() for l in record['Labels'].split(",")]
        recipes[record['Name']] = record

    console.print(f"Read {record_count} recipes ({len(recipes)} unique) from [yellow]{filename.name}[/]")

    return recipes

def generate_mealplan(recipes, num_weeks: int):
    # Compose mealplan
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
            menu = random.choice([ r for r in recipes.values() if constraint(r) ])
            menu['date'] = start_date.shift(days=day_offset)
            menu['Datum'] = menu['date'].format('MMM D, YYYY')
            menu['Gedaan'] = "No"
            # choice['match'] = label
            menu['Weekd'] = ""
            menu['Weekdag'] = ""
            mealplan.append(recipes.pop(menu['Name']))
            day_offset += 1
    return mealplan


@click.command()
@click.option('--recipes-filename', "-r", help='CSV file containing recipies to generate a mealplan from', 
              type=click.File(mode='r', encoding=None, errors='strict', lazy=None, atomic=False))
@click.option('--num-weeks', "-w", help='Number of weeks', default=1)
@click.option('--export', "-e", help='Export as CSV', default=False, is_flag=True)
def main(recipes_filename, num_weeks, export):
    """Simple program that greets NAME for a total of COUNT times."""
    recipes = import_recipes(recipes_filename)
    mealplan = generate_mealplan(recipes, num_weeks)
    
    if export:
        export_mealplan(mealplan)

    print_mealplan(mealplan)

    

if __name__ == '__main__':
    main()
