

import json
import random
import os
import click

@click.command()
def main():
    """Show a random Git tip from tips.json"""
    # Determine the path to tips.json
    dir_path = os.path.dirname(os.path.abspath(__file__))
    tips_path = os.path.join(dir_path, 'tips.json')

    try:
        with open(tips_path, 'r', encoding='utf-8') as f:
            tips = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        click.echo("⚠️ Failed to load tips.json. Please make sure the file exists and is valid.")
        return

    if not tips:
        click.echo("⚠️ No tips found in tips.json.")
        return

    tip = random.choice(tips)
    click.echo(f"📌 {tip['command']}\n{tip['description']}")

if __name__ == "__main__":
    main()