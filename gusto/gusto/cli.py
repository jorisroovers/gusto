
from .mealplan import MealPlan, Recipes

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
    table.add_column("Tags", justify="right")

    for i, meal in enumerate(mealplan):
        # labels_str = choice['Labels'].replace(choice['match'], f"[b][u]{choice['match']}[/][/]")
        table.add_row(meal.date.format('dddd'), meal.date.format('YYYY-MM-DD'), 
                      meal.recipe['Name'], meal.recipe['Tags'])
        
        # Add empty row after each week
        if ((meal.date.format('dddd') == "Sunday") and (i != len(mealplan)-1)):
            table.add_row()

    console.print(table)


@click.command()
@click.option('--recipes-filename', "-r", help='CSV file containing recipes to generate a mealplan from', 
              type=click.Path(exists=True,file_okay=True, dir_okay=False, readable=True, resolve_path=True))
@click.option('--num-weeks', "-w", help='Number of weeks', default=1)
@click.option('--export', "-e", help='Export as CSV', default=False, is_flag=True)
def main(recipes_filename, num_weeks, export):
    """ Gusto. Mealplanner."""
    recipes = Recipes()
    
    recipes.import_from_csv(recipes_filename)

    mealplan = MealPlan(recipes)
    mealplan.generate_mealplan(num_weeks)
    
    if export:
        timestamp = arrow.now().format('YYYY-MM-DD_HH-mm-ss')
        export_filename = f"gusto-export-{timestamp}.csv"
        mealplan.export_to_csv(export_filename)

    print_mealplan(mealplan.mealplan)

    
if __name__ == '__main__':
    main()
