
import csv
import random

import arrow
import click
from rich.console import Console
from rich.table import Table


@click.command()
@click.option('--recipes-filename', "-r", help='CSV file containing recipies to generate a mealplan from', 
              type=click.File(mode='r', encoding=None, errors='strict', lazy=None, atomic=False))
@click.option('--num-weeks', "-w", help='Number of weeks', default=1)
@click.option('--export', "-e", help='Export as CSV', default=False, is_flag=True)
def main(recipes_filename, num_weeks, export):
    """Simple program that greets NAME for a total of COUNT times."""
    console = Console()
    
    # Parse CSV
    recipes = {}
    records = csv.DictReader(recipes_filename)
    record_count = 0
    for record in records:
        record_count+=1
        record['parsed-labels'] = [l.strip() for l in record['Labels'].split(",")]
        recipes[record['Name']] = record

    console.print(f"Read {record_count} recipes ({len(recipes)} unique) from [yellow]{recipes_filename.name}[/]")


    # Compose menu
    choices = []
    start_date  = arrow.utcnow().shift(weekday=0)
    day_offset = 0
    for _ in range(num_weeks):
        # add some randomness to when we eat what, but ensure Friday is "Zondigen"
        required_labels = ["Vegetarisch", "Vis", "Asian", "Steak", "Pasta", "*"]
        random.shuffle(required_labels)
        required_labels.insert(4, "Zondigen")
        
        for label in required_labels:
            choice = random.choice([ r for r in recipes.values() if label == "*" or label in r['parsed-labels'] ])
            choice['date'] = start_date.shift(days=day_offset)
            choice['Datum'] = choice['date'].format('MMM D, YYYY')
            choice['Gedaan'] = "No"
            choice['match'] = label
            choice['Weekd'] = ""
            choice['Weekdag'] = ""
            choices.append(recipes.pop(choice['Name']))
            day_offset += 1

    # Export to CSV
    if export:
        timestamp = arrow.now().format('YYYY-MM-DD_HH-mm-ss')
        export_filename = f"gusto-export-{timestamp}.csv"
        console.print(f"Exporting to [yellow]{export_filename}[/]")

        with open(export_filename, 'w') as export_file:
            fieldnames = ["Gedaan", "Weekd", "Datum", "Name", "Labels", "Comments", "URL", "Score", "Weekdag", 
                          "Related to Planned meals (Column)" ]
            exporter = csv.DictWriter(export_file, fieldnames=fieldnames, extrasaction="ignore")
            exporter.writeheader()
            exporter.writerows(choices)

    # Pretty print to console
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Weekday", style="dim", width=12)
    table.add_column("Date", style="dim")
    table.add_column("Recipe")
    table.add_column("Labels", justify="right")

    for i, choice in enumerate(choices):
        labels_str = choice['Labels'].replace(choice['match'], f"[b][u]{choice['match']}[/][/]")
        table.add_row(choice['date'].format('dddd'), choice['date'].format('YYYY-MM-DD'), 
                      choice['Name'], labels_str)
        
        # Add empty row after each week
        if ((choice['date'].format('dddd') == "Sunday") and (i != len(choices)-1)):
            table.add_row()

    console.print(table)

if __name__ == '__main__':
    main()
