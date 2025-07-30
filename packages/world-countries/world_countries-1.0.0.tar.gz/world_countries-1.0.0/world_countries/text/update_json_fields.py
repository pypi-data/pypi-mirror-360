#!/usr/bin/env python3
"""
Скрипт для обновления полей в JSON файле на основе данных из CSV файла.
Заменяет поля: name -> CountryName, capital -> Capital, continent -> Continent, region -> Region
"""

import json
import csv
import sys
import argparse
from typing import Dict, List, Any


def load_json_file(json_path: str) -> List[Dict[str, Any]]:
    """Загружает JSON файл"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Файл {json_path} не найден")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Ошибка: Неверный формат JSON в файле {json_path}: {e}")
        sys.exit(1)


def load_csv_file(csv_path: str) -> Dict[int, Dict[str, str]]:
    """Загружает CSV файл и создает словарь с данными по ID"""
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = {}
            for row in reader:
                country_id = int(row['ID'])
                data[country_id] = {
                    'CountryName': row['CountryName'],
                    'Capital': row['Capital'],
                    'Continent': row['Continent'],
                    'Region': row['Region']
                }
            return data
    except FileNotFoundError:
        print(f"Ошибка: Файл {csv_path} не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при чтении CSV файла {csv_path}: {e}")
        sys.exit(1)


def update_json_fields(json_data: List[Dict[str, Any]], csv_data: Dict[int, Dict[str, str]]) -> List[Dict[str, Any]]:
    """Обновляет поля в JSON данных на основе CSV данных"""
    updated_data = []
    
    for country in json_data:
        country_id = country.get('id')
        if country_id in csv_data:
            # Создаем копию страны с обновленными полями
            updated_country = country.copy()
            
            # Обновляем поля согласно маппингу
            csv_row = csv_data[country_id]
            updated_country['name'] = csv_row['CountryName']
            updated_country['capital'] = csv_row['Capital']
            updated_country['continent'] = csv_row['Continent']
            updated_country['region'] = csv_row['Region']
            
            updated_data.append(updated_country)
        else:
            # Если ID не найден в CSV, оставляем как есть
            updated_data.append(country)
    
    return updated_data


def save_json_file(data: List[Dict[str, Any]], output_path: str):
    """Сохраняет JSON данные в файл"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Обновленный JSON сохранен в: {output_path}")
    except Exception as e:
        print(f"Ошибка при сохранении файла {output_path}: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Обновляет поля в JSON файле на основе данных из CSV файла'
    )
    parser.add_argument('json_input', help='Путь к входному JSON файлу')
    parser.add_argument('csv_input', help='Путь к входному CSV файлу')
    parser.add_argument('json_output', help='Путь к выходному JSON файлу')
    
    args = parser.parse_args()
    
    # Загружаем данные
    print(f"Загружаем JSON файл: {args.json_input}")
    json_data = load_json_file(args.json_input)
    
    print(f"Загружаем CSV файл: {args.csv_input}")
    csv_data = load_csv_file(args.csv_input)
    
    print(f"Найдено {len(json_data)} стран в JSON")
    print(f"Найдено {len(csv_data)} стран в CSV")
    
    # Обновляем поля
    print("Обновляем поля...")
    updated_data = update_json_fields(json_data, csv_data)
    
    # Сохраняем результат
    save_json_file(updated_data, args.json_output)
    
    # Статистика
    updated_count = sum(1 for country in updated_data if country.get('id') in csv_data)
    print(f"Обновлено {updated_count} стран")


if __name__ == "__main__":
    main() 