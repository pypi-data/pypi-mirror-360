from glob import glob
from os.path import isdir, isfile, realpath, dirname, join
import json

class all_countries:
    """To get the details of all countries in the world

    Example:
        country = all_countries()  # English (default)
        country = all_countries(language='ru')  # Russian
        country = all_countries(language='fr')  # French
    """
    def __init__(self, language='en'):
        """constructor method"""
        self.language = language
        dir_path = dirname(realpath(__file__))
        data_path = join(dir_path, 'data')
        
        # Select files based on language
        if language == 'ru':
            countries_file_path = join(data_path, 'countries_ru.json')
        elif language == 'fr':
            countries_file_path = join(data_path, 'countries_fr.json')
        elif language == 'es':
            countries_file_path = join(data_path, 'countries_es.json')
        elif language == 'de':
            countries_file_path = join(data_path, 'countries_de.json')
        elif language == 'ch':
            countries_file_path = join(data_path, 'countries_ch.json')
        elif language == 'ar':
            countries_file_path = join(data_path, 'countries_ar.json')
        else:
            countries_file_path = join(data_path, 'countries_en.json')
        
        # Load data
        with open(countries_file_path, encoding='utf-8') as file:
            countries_file = json.load(file)
            self.countries_file = countries_file

        # Create a list of countries in the selected language
        self.country_list = [country['name'] for country in self.countries_file]

    def countries(self):
        """Returns all the available countries in the world.
        :return: list
        """
        return self.country_list

    def phone_code(self):
        """Returns the countries and their Phone codes.
        :return: dict
        """
        phonecode_dict = {}
        for country in self.countries_file:
            phonecode_dict[country['name']] = country['phone_code']
        return phonecode_dict

    def currencies(self):
        """Returns the countries and their Currencies.
        :return: dict
        """
        currency_dict = {}
        for country in self.countries_file:
            currency_dict[country['name']] = country['currency']
        return currency_dict
    
    def languages(self):
        """Returns the countries and their languages.
        :return: dict
        """
        languages_dict = {}
        for country in self.countries_file:
            languages_dict[country['name']] = country['languages']
        return languages_dict

    def get_languages_by_country(self, country_name):
        """Returns languages for a specific country.
        :param country_name: str - name of the country
        :return: list or None
        """
        for country in self.countries_file:
            if country['name'] == country_name:
                return country['languages']
        return None
    
    def search_by_language(self, language_code):
        """Returns all countries that speak a specific language.
        :param language_code: str - language code (e.g., 'en', 'fr', 'es')
        :return: list
        """
        countries_with_language = []
        for country in self.countries_file:
            if language_code in country['languages']:
                countries_with_language.append(country['name'])
        return countries_with_language

    def capitals(self):
        """Returns the countries and their capitals.
        :return: dict
        """
        capital_dict = {}
        for country in self.countries_file:
            capital_dict[country['name']] = country['capital']
        return capital_dict
            
    def continents(self):
        """Returns the countries with their continents.
        :return: dict
        """
        continent_dict = {}
        for country in self.countries_file:
            continent_dict[country['name']] = country['continent']
        return continent_dict

    def regions(self):
        """Returns the countries with their regions.
        :return: dict
        """
        region_dict = {}
        for country in self.countries_file:
            region_dict[country['name']] = country['region']
        return region_dict

    def countries_in_continents(self):
        """Returns the list of countries under continents.
        :return: dict
        """
        continents_dict = {}
        
        for country in self.countries_file:
            continent = country['continent']
            if continent not in continents_dict:
                continents_dict[continent] = []
            continents_dict[continent].append(country['name'])
        
        return continents_dict
    
    def countries_in_region(self):
        """Returns the list of countries in a region.
        :return: dict
        """
        region_dict = {}
        
        for country in self.countries_file:
            region = country['region']
            if region not in region_dict:
                region_dict[region] = []
            region_dict[region].append(country['name'])
        
        return region_dict

    def get_country_info(self, country_name):
        """Returns complete information about a specific country.
        :param country_name: str - name of the country
        :return: dict or None
        """
        for country in self.countries_file:
            if country['name'] == country_name:
                return country
        return None

    def search_by_continent(self, continent):
        """Returns all countries in a specific continent.
        :param continent: str - name of the continent
        :return: list
        """
        return [country['name'] for country in self.countries_file 
                if country['continent'] == continent]

    def search_by_region(self, region):
        """Returns all countries in a specific region.
        :param region: str - name of the region
        :return: list
        """
        return [country['name'] for country in self.countries_file 
                if country['region'] == region]