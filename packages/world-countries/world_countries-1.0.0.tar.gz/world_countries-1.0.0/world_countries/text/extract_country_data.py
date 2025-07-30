#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для извлечения данных о странах из JSON файлов
и сохранения их в единый файл с полями: id, name, capital, continent, region
"""

import json
import os
from pathlib import Path

def extract_country_data():
    """
    Извлекает данные о странах из всех JSON файлов в папке data
    и сохраняет их в единый файл
    """
    
    # Путь к папке с данными
    data_dir = Path("world_countries/data")
    
    # Список всех JSON файлов с данными о странах
    json_files = [
        "countries_en.json",
        "countries_de.json", 
        "countries_fr.json",
        "countries_es.json",
        "countries_ru.json",
        "countries_ar.json",
        "countries_ch.json"
    ]
    
    # Словарь для хранения данных по ID
    countries_data = {}
    
    # Обрабатываем каждый JSON файл
    for json_file in json_files:
        file_path = data_dir / json_file
        language = json_file.split('_')[1].split('.')[0]  # Извлекаем язык из имени файла
        
        if file_path.exists():
            print(f"Обрабатываю файл: {json_file}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Обрабатываем каждую страну
                for country in data:
                    country_id = country.get('id')
                    
                    if country_id not in countries_data:
                        countries_data[country_id] = {
                            'id': country_id,
                            'name': {},
                            'capital': country.get('capital', ''),
                            'continent': country.get('continent', ''),
                            'region': country.get('region', '')
                        }
                    
                    # Добавляем название на соответствующем языке
                    countries_data[country_id]['name'][language] = country.get('name', '')
                    
            except Exception as e:
                print(f"Ошибка при обработке файла {json_file}: {e}")
        else:
            print(f"Файл не найден: {file_path}")
    
    # Сортируем данные по ID
    sorted_countries = sorted(countries_data.values(), key=lambda x: x['id'])
    
    # Сохраняем результат в JSON файл
    output_file = "countries_extracted.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_countries, f, ensure_ascii=False, indent=2)
    
    print(f"\nДанные сохранены в файл: {output_file}")
    print(f"Всего обработано стран: {len(sorted_countries)}")
    
    # Выводим первые несколько записей для проверки
    print("\nПервые 5 записей:")
    for i, country in enumerate(sorted_countries[:5]):
        print(f"{i+1}. ID: {country['id']}")
        print(f"   Названия: {country['name']}")
        print(f"   Столица: {country['capital']}")
        print(f"   Континент: {country['continent']}")
        print(f"   Регион: {country['region']}")
        print()

def create_simple_csv():
    """
    Создает простой CSV файл с основными данными на английском языке
    """
    import csv
    
    # Загружаем данные из английского файла
    en_file = Path("world_countries/data/countries_en.json")
    
    if en_file.exists():
        with open(en_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Сортируем по ID
        sorted_data = sorted(data, key=lambda x: x['id'])
        
        # Сохраняем в CSV
        csv_file = "countries_simple.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Capital', 'Continent', 'Region'])
            
            for country in sorted_data:
                writer.writerow([
                    country['id'],
                    country['name'],
                    country['capital'],
                    country['continent'],
                    country['region']
                ])
        
        print(f"Простой CSV файл создан: {csv_file}")

if __name__ == "__main__":
    print("Начинаю извлечение данных о странах...")
    extract_country_data()
    print("\nСоздаю простой CSV файл...")
    create_simple_csv()
    print("\nГотово!") 