import click
from subcli.get_subtitle import search_subtitle_options, get_subtitle_options, download_subtitle
from InquirerPy import inquirer

@click.command()
@click.argument('movie')
def subcli(movie):
    results = search_subtitle_options(movie)

    if not results:
        click.echo("No results found.")
        return
    click.echo("Available websites:")
    titles = list(results.keys())
    
    selection = inquirer.select(
        message="Select a subtitle result:",
        default=titles[0],
        choices=titles,
        pointer='=>',
        instruction='Use arrow keys to navigate and Enter to select.',
    ).execute()

    url = results[selection][0]
    languages = get_subtitle_options(url)
    choices = list(languages.keys())

    selection = inquirer.select(
        message="Select a subtitle language:",
        default=choices[0],
        choices=choices,
        pointer='=>',
        instruction='Use arrow keys to navigate and Enter to select.',
    ).execute()

    click.secho(f"You selected: {selection}", fg="green")

    link = languages[selection]
    file = download_subtitle(link)
    click.secho(f"File downloaded as: {file}", fg="blue")

if __name__ == '__main__':
    subcli()