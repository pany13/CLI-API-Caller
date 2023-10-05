import os # Used to clear the CLI
import click # A library that simplifies the process of creating and interacting with CLI interfaces
import requests # Used to call APIs
import json # Used for working with JSON formatted text
import time # Used for the "loading bar"

API_URL_COUNTRY = 'https://restcountries.com/v3.1/name/'
API_URL_WEATHER = 'https://wttr.in/'

def get_capital(city_list):
    for city in city_list:
        if city.get('capital', False):
            return city['capital'][0]
    return None

def display_country_info(country_data):
    # Choose what information to extract from the API
    common_info = {
        'Name': country_data[0].get('name', {}).get('official'),
        'Capital': ', '.join(country_data[0].get('capital', ['N/A'])),
        'Population': country_data[0].get('population', 'N/A'),
        'Region': country_data[0].get('region', 'N/A'),
        'Subregion': country_data[0].get('subregion', 'N/A'),
        'Languages': ', '.join(lang_name for lang_name in country_data[0].get('languages', {}).values()),
    }
    
    # Display common information to the user
    click.echo('Common Information:')
    for key, value in common_info.items():
        click.echo(f'{key}: {value}')

    # Get weather of the searched countries capital
    capital = get_capital(country_data)
    if capital:
        # Display weather information for the capital
        click.echo(f'\nAdditional information:\nWeather Information for {capital}:')
        weather_url = f'{API_URL_WEATHER}{capital}?format=%C+%t+%w'
        weather_response = requests.get(weather_url)
        if weather_response.status_code == 200:
            weather_data = weather_response.text.strip()
            click.echo(weather_data)
        else:
            click.echo('Weather information is not available for the capital.')
    else:
        click.echo('Capital information is not available.')

def welcome_message():
    welcome = """
 _______  _______  __   __  __    _  _______  ______    __   __  
|       ||       ||  | |  ||  |  | ||       ||    _ |  |  | |  | 
|       ||   _   ||  | |  ||   |_| ||_     _||   | ||  |  |_|  | 
|       ||  | |  ||  |_|  ||       |  |   |  |   |_||_ |       | 
|      _||  |_|  ||       ||  _    |  |   |  |    __  ||_     _| 
|     |_ |       ||       || | |   |  |   |  |   |  | |  |   |   
|_______||_______||_______||_|  |__|  |___|  |___|  |_|  |___|   
                                 ___   __    _  _______  _______ 
                                |   | |  |  | ||       ||       |
                                |   | |   |_| ||    ___||   _   |
                                |   | |       ||   |___ |  | |  |
                                |   | |  _    ||    ___||  |_|  |
 _____   _____   _____   _____  |   | | | |   ||   |    |       |
|_____| |_____| |_____| |_____| |___| |_|  |__||___|    |_______|
    """
    click.echo(welcome)
    click.echo("            Welcome to the Country Information App!\n")

def animated_loading():
    click.echo('\n')
    for i in range(40):
        time.sleep(0.095)
        click.echo(f'           [{"=" * i}{" " * (39 - i)}]', nl=False)
        click.echo('\r', nl=False)
    click.echo('\n')

@click.command()
@click.option('--output', '-o', type=click.File('w', encoding='utf-8'), default='saved_search_info.txt', help='Output file')
def fetch_country_info(output):
    try:
        # Clear screen no matter what OS
        os.system('cls' if os.name == 'nt' else 'clear')
        # Display welcome message
        welcome_message()

        while True:
            # Prompt the user for a country name
            country_name = click.prompt(' > > > Enter a country name').lower()

            # Get country information
            response = requests.get(API_URL_COUNTRY + country_name)

            # If the API responds with error code 404: "country not found"
            if response.status_code == 404:
                try_again = click.confirm(f"Country '{country_name}' doesn't exist. Do you want to try again? (yes/no)", default=True)
                if not try_again:
                    break
                continue  # Go back to prompting for a new country name

            response.raise_for_status()
            country_data = response.json()

            # Display animated loading bar to (hopefully) give both of the APIs some time to respond before the result is asked to get printed on the screen
            animated_loading()

            # Display the chosen information from the API to the user
            display_country_info(country_data)

            # Ask the user if they want to save the information to a file
            save_to_file = click.confirm('Do you want to save the common information to a file?', default=True)
            if save_to_file:
                # Write country_data to the output file
                json.dump(country_data, output, ensure_ascii=False, indent=4)
                click.echo(f'All the information from the searched country ({country_name}) has been written to {output.name}')

            # Does the user want to do another search?
            another_search = click.confirm('Do you want to perform another search?', default=True)
            if not another_search:
                break

            # Handle errors
    except requests.exceptions.RequestException as e:
        click.echo(f'Error: {e}')
    except Exception as e:
        click.echo(f'An error occurred: {e}')

if __name__ == '__main__':
    fetch_country_info()
