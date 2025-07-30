from world_countries.countries import all_countries

# Create an instance for Arabic language
_wc_instance = all_countries(language='ar')

# Export all methods as module functions
def countries():
    return _wc_instance.countries()

def phone_code():
    return _wc_instance.phone_code()

def currencies():
    return _wc_instance.currencies()

def languages():
    return _wc_instance.languages()

def get_languages_by_country(country_name):
    return _wc_instance.get_languages_by_country(country_name)

def search_by_language(language_code):
    return _wc_instance.search_by_language(language_code)

def capitals():
    return _wc_instance.capitals()

def continents():
    return _wc_instance.continents()

def regions():
    return _wc_instance.regions()

def countries_in_continents():
    return _wc_instance.countries_in_continents()

def countries_in_region():
    return _wc_instance.countries_in_region()

def get_country_info(country_name):
    return _wc_instance.get_country_info(country_name)

def search_by_continent(continent):
    return _wc_instance.search_by_continent(continent)

def search_by_region(region):
    return _wc_instance.search_by_region(region)