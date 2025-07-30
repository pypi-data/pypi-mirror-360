import json
from pathlib import Path
from typing import Union

import phonenumbers
import pycountry
import pytz
from timezonefinder import TimezoneFinder
from babel import Locale
from ..network.ip_info import get_network_configuration_by_proxy






def generate_geo_params(phone_data: dict) -> dict:
    """
    Генерирует географические параметры (локаль, часовой пояс и др.)
    на основе входных данных о сети и стране.

    :param phone_data: Словарь с данными, должен содержать 'country_code' (ISO)
                       и опционально 'phone_code'.
    :return: Словарь с сгенерированными параметрами или None в случае ошибки.
    """
    country_iso = phone_data.get('country_code')
    if not country_iso:
        print("Ошибка: в исходных данных отсутствует 'country_code'.")
        return None

    try:
        # 1. Получаем объект страны из pycountry по ISO коду
        country = pycountry.countries.get(alpha_2=country_iso)
        if not country:
            print(f"Ошибка: не удалось найти страну по коду ISO '{country_iso}'.")
            return None

        country_name = country.name

        # 2. Определяем основной язык и формируем локаль
        primary_language_code = None
        if hasattr(country, 'languages'):
            primary_language_code = country.languages[0].alpha_2

        if not primary_language_code:
            phone_code = phone_data.get('phone_code')
            if phone_code:
                region_code = phonenumbers.region_code_for_country_code(int(phone_code))
                locale_obj = Locale.parse(f"und_{region_code}")
                primary_language_code = locale_obj.language

        if not primary_language_code:
            print(f"Предупреждение: не удалось определить основной язык для {country_iso}. Используется 'en'.")
            primary_language_code = 'en'

        locale = f"{primary_language_code.lower()}-{country_iso.upper()}"

        # 3. Определяем основной часовой пояс с помощью Pytz
        # pytz.country_timezones - это словарь {'ISO_КОД': ['Таймзона1', 'Таймзона2', ...]}
        timezones = pytz.country_timezones.get(country_iso)

        primary_timezone = None
        if timezones:
            # Первый в списке обычно является наиболее распространенным
            primary_timezone = timezones[0]
        else:
            # Запасной вариант, если pytz не знает о такой стране
            print(f"Предупреждение: не удалось найти часовой пояс для {country_iso} в pytz. Пробуем UTC.")
            # Это маловероятно для реальных стран, но лучше иметь запасной вариант
            primary_timezone = 'UTC'

        return {
            "locale": locale,
            "timezone": primary_timezone,
            "country_iso": country_iso,
            "country_name": country_name
        }

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None


for _ in range(5):
    get_prop_by_ip('82.163.172.61:50101')