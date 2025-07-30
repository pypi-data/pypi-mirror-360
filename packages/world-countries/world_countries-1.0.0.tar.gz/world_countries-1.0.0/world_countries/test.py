import unittest
import world_countries as wc
from world_countries.countries import all_countries


class TestAllCountries(unittest.TestCase):
    """Tests for the all_countries class"""
    
    def setUp(self):
        """Test setup"""
        self.countries_en = all_countries('en')
        self.countries_ru = all_countries('ru')
        self.countries_fr = all_countries('fr')
    
    def test_init_default_language(self):
        """Test initialization with default language"""
        countries = all_countries()
        self.assertEqual(countries.language, 'en')
        self.assertIsInstance(countries.countries_file, list)
        self.assertIsInstance(countries.country_list, list)
        self.assertGreater(len(countries.country_list), 0)
    
    def test_init_different_languages(self):
        """Test initialization with different languages"""
        languages = ['en', 'ru', 'fr', 'es', 'de','ch', 'ar']
        for lang in languages:
            countries = all_countries(lang)
            self.assertEqual(countries.language, lang)
            self.assertIsInstance(countries.countries_file, list)
            self.assertGreater(len(countries.countries_file), 0)
    
    def test_countries_method(self):
        """Test countries() method"""
        countries_list = self.countries_en.countries()
        self.assertIsInstance(countries_list, list)
        self.assertGreater(len(countries_list), 0)
        # Check that all elements are strings
        for country in countries_list:
            self.assertIsInstance(country, str)
        # Check for known countries
        self.assertIn('United States', countries_list)
        self.assertIn('Russia', countries_list)
        self.assertIn('China', countries_list)
    
    def test_phone_code_method(self):
        """Test phone_code() method"""
        phone_codes = self.countries_en.phone_code()
        self.assertIsInstance(phone_codes, dict)
        self.assertGreater(len(phone_codes), 0)
        # Check specific codes
        self.assertEqual(phone_codes['United States'], '1')
        self.assertEqual(phone_codes['Russia'], '7')
        self.assertEqual(phone_codes['China'], '86')
        # Check that all values are strings
        for code in phone_codes.values():
            self.assertIsInstance(code, str)
    
    def test_currencies_method(self):
        """Test currencies() method"""
        currencies = self.countries_en.currencies()
        self.assertIsInstance(currencies, dict)
        self.assertGreater(len(currencies), 0)
        # Check specific currencies
        self.assertEqual(currencies['United States'], 'USD')
        self.assertEqual(currencies['Russia'], 'RUB')
        self.assertEqual(currencies['China'], 'CNY')
        # Check that all values are strings
        for currency in currencies.values():
            self.assertIsInstance(currency, str)
    
    def test_languages_method(self):
        """Test languages() method"""
        languages = self.countries_en.languages()
        self.assertIsInstance(languages, dict)
        self.assertGreater(len(languages), 0)
        # Check specific languages
        self.assertIn('en', languages['United States'])
        self.assertIn('ru', languages['Russia'])
        self.assertIn('zh', languages['China'])
        # Check that all values are lists
        for lang_list in languages.values():
            self.assertIsInstance(lang_list, list)
    
    def test_get_languages_by_country_existing(self):
        """Test get_languages_by_country() method for existing country"""
        languages = self.countries_en.get_languages_by_country('United States')
        self.assertIsInstance(languages, list)
        self.assertIn('en', languages)
        
        languages = self.countries_en.get_languages_by_country('Russia')
        self.assertIsInstance(languages, list)
        self.assertIn('ru', languages)
    
    def test_get_languages_by_country_nonexistent(self):
        """Test get_languages_by_country() method for non-existent country"""
        languages = self.countries_en.get_languages_by_country('NonExistentCountry')
        self.assertIsNone(languages)
    
    def test_search_by_language_existing(self):
        """Test search_by_language() method for existing language"""
        countries = self.countries_en.search_by_language('en')
        self.assertIsInstance(countries, list)
        self.assertGreater(len(countries), 0)
        self.assertIn('United States', countries)
        self.assertIn('United Kingdom', countries)
        
        countries = self.countries_en.search_by_language('ru')
        self.assertIsInstance(countries, list)
        self.assertIn('Russia', countries)
    
    def test_search_by_language_nonexistent(self):
        """Test search_by_language() method for non-existent language"""
        countries = self.countries_en.search_by_language('xyz')
        self.assertIsInstance(countries, list)
        self.assertEqual(len(countries), 0)
    
    def test_capitals_method(self):
        """Test capitals() method"""
        capitals = self.countries_en.capitals()
        self.assertIsInstance(capitals, dict)
        self.assertGreater(len(capitals), 0)
        # Check specific capitals
        self.assertEqual(capitals['United States'], 'Washington')
        self.assertEqual(capitals['Russia'], 'Moscow')
        self.assertEqual(capitals['China'], 'Beijing')
        # Check that all values are strings
        for capital in capitals.values():
            self.assertIsInstance(capital, str)
    
    def test_continents_method(self):
        """Test continents() method"""
        continents = self.countries_en.continents()
        self.assertIsInstance(continents, dict)
        self.assertGreater(len(continents), 0)
        # Check specific continents
        self.assertEqual(continents['United States'], 'North America')
        self.assertEqual(continents['Russia'], 'Europe')
        self.assertEqual(continents['China'], 'Asia')
        # Check that all values are strings
        for continent in continents.values():
            self.assertIsInstance(continent, str)
    
    def test_regions_method(self):
        """Test regions() method"""
        regions = self.countries_en.regions()
        self.assertIsInstance(regions, dict)
        self.assertGreater(len(regions), 0)
        # Check specific regions
        self.assertEqual(regions['United States'], 'North America')
        self.assertEqual(regions['Russia'], 'Eastern Europe')
        self.assertEqual(regions['China'], 'Eastern Asia')
        # Check that all values are strings
        for region in regions.values():
            self.assertIsInstance(region, str)
    
    def test_countries_in_continents_method(self):
        """Test countries_in_continents() method"""
        continents_dict = self.countries_en.countries_in_continents()
        self.assertIsInstance(continents_dict, dict)
        self.assertGreater(len(continents_dict), 0)
        
        # Check for major continents
        self.assertIn('North America', continents_dict)
        self.assertIn('Europe', continents_dict)
        self.assertIn('Asia', continents_dict)
        self.assertIn('Africa', continents_dict)
        self.assertIn('South America', continents_dict)
        self.assertIn('Oceania', continents_dict)
        
        # Check that all values are lists
        for country_list in continents_dict.values():
            self.assertIsInstance(country_list, list)
            self.assertGreater(len(country_list), 0)
        
        # Check specific countries in continents
        self.assertIn('United States', continents_dict['North America'])
        self.assertIn('Russia', continents_dict['Europe'])
        self.assertIn('China', continents_dict['Asia'])
    
    def test_countries_in_region_method(self):
        """Test countries_in_region() method"""
        regions_dict = self.countries_en.countries_in_region()
        self.assertIsInstance(regions_dict, dict)
        self.assertGreater(len(regions_dict), 0)
        
        # Check that all values are lists
        for country_list in regions_dict.values():
            self.assertIsInstance(country_list, list)
            self.assertGreater(len(country_list), 0)
        
        # Check specific regions
        self.assertIn('North America', regions_dict)
        self.assertIn('Eastern Europe', regions_dict)
        self.assertIn('Eastern Asia', regions_dict)
    
    def test_get_country_info_existing(self):
        """Test get_country_info() method for existing country"""
        country_info = self.countries_en.get_country_info('United States')
        self.assertIsInstance(country_info, dict)
        self.assertEqual(country_info['name'], 'United States')
        self.assertEqual(country_info['capital'], 'Washington')
        self.assertEqual(country_info['currency'], 'USD')
        self.assertIn('en', country_info['languages'])
        
        country_info = self.countries_en.get_country_info('Russia')
        self.assertIsInstance(country_info, dict)
        self.assertEqual(country_info['name'], 'Russia')
        self.assertEqual(country_info['capital'], 'Moscow')
        self.assertEqual(country_info['currency'], 'RUB')
        self.assertIn('ru', country_info['languages'])
    
    def test_get_country_info_nonexistent(self):
        """Test get_country_info() method for non-existent country"""
        country_info = self.countries_en.get_country_info('NonExistentCountry')
        self.assertIsNone(country_info)
    
    def test_search_by_continent_existing(self):
        """Test search_by_continent() method for existing continent"""
        countries = self.countries_en.search_by_continent('North America')
        self.assertIsInstance(countries, list)
        self.assertGreater(len(countries), 0)
        self.assertIn('United States', countries)
        self.assertIn('Canada', countries)
        
        countries = self.countries_en.search_by_continent('Europe')
        self.assertIsInstance(countries, list)
        self.assertGreater(len(countries), 0)
        self.assertIn('Russia', countries)
        self.assertIn('Germany', countries)
    
    def test_search_by_continent_nonexistent(self):
        """Test search_by_continent() method for non-existent continent"""
        countries = self.countries_en.search_by_continent('NonExistentContinent')
        self.assertIsInstance(countries, list)
        self.assertEqual(len(countries), 0)
    
    def test_search_by_region_existing(self):
        """Test search_by_region() method for existing region"""
        countries = self.countries_en.search_by_region('North America')
        self.assertIsInstance(countries, list)
        self.assertGreater(len(countries), 0)
        self.assertIn('United States', countries)
        self.assertIn('Canada', countries)
        
        countries = self.countries_en.search_by_region('Eastern Europe')
        self.assertIsInstance(countries, list)
        self.assertGreater(len(countries), 0)
        self.assertIn('Russia', countries)
    
    def test_search_by_region_nonexistent(self):
        """Test search_by_region() method for non-existent region"""
        countries = self.countries_en.search_by_region('NonExistentRegion')
        self.assertIsInstance(countries, list)
        self.assertEqual(len(countries), 0)
    
    def test_different_languages_data_consistency(self):
        """Test data consistency between different languages"""
        # Check that the number of countries is the same for all languages
        en_count = len(self.countries_en.countries())
        ru_count = len(self.countries_ru.countries())
        fr_count = len(self.countries_fr.countries())
        
        self.assertEqual(en_count, ru_count)
        self.assertEqual(en_count, fr_count)
        
        # Check that major countries are present in all languages
        # (names may differ, but the count should be the same)
        en_phone_codes = self.countries_en.phone_code()
        ru_phone_codes = self.countries_ru.phone_code()
        fr_phone_codes = self.countries_fr.phone_code()
        
        self.assertEqual(len(en_phone_codes), len(ru_phone_codes))
        self.assertEqual(len(en_phone_codes), len(fr_phone_codes))
    
    def test_data_integrity(self):
        """Test data integrity"""
        # Check that all methods return data for all countries
        countries_list = self.countries_en.countries()
        phone_codes = self.countries_en.phone_code()
        currencies = self.countries_en.currencies()
        capitals = self.countries_en.capitals()
        continents = self.countries_en.continents()
        regions = self.countries_en.regions()
        
        # All dictionaries should contain the same number of keys
        self.assertEqual(len(countries_list), len(phone_codes))
        self.assertEqual(len(countries_list), len(currencies))
        self.assertEqual(len(countries_list), len(capitals))
        self.assertEqual(len(countries_list), len(continents))
        self.assertEqual(len(countries_list), len(regions))
        
        # Check that all countries are present in all dictionaries
        for country in countries_list:
            self.assertIn(country, phone_codes)
            self.assertIn(country, currencies)
            self.assertIn(country, capitals)
            self.assertIn(country, continents)
            self.assertIn(country, regions)
    
    def test_edge_cases(self):
        """Test edge cases"""
        # Test with empty string
        languages = self.countries_en.get_languages_by_country('')
        self.assertIsNone(languages)
        
        # Test with None
        languages = self.countries_en.get_languages_by_country(None)
        self.assertIsNone(languages)
        
        # Test search by empty language
        countries = self.countries_en.search_by_language('')
        self.assertIsInstance(countries, list)
        
        # Test search by empty continent
        countries = self.countries_en.search_by_continent('')
        self.assertIsInstance(countries, list)
        
        # Test search by empty region
        countries = self.countries_en.search_by_region('')
        self.assertIsInstance(countries, list)


if __name__ == '__main__':
    unittest.main()