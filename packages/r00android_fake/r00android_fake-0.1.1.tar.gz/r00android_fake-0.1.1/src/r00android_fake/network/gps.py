import requests
from pprint import pprint
import random

# ... (данные для примера остаются без изменений)
input_data_att = {
    'ip': '82.163.172.61',
    'timezone': 'America/New_York',
}

input_data_no_ip = {
    'timezone': 'Europe/Berlin',
    'ip': None
}


def _add_realism_to_coords(lat: float, lon: float) -> tuple[str, str]:
    """
    Добавляет небольшое случайное смещение к координатам и форматирует их
    с реалистичным количеством знаков после запятой.
    """
    # Смещение примерно до 15 метров. 0.0001 градуса ~ 11.1 метра.
    # Мы берем чуть больше для большего разброса.
    radius = 0.00015

    # Генерируем случайное смещение
    random_lat_offset = random.uniform(-radius, radius)
    random_lon_offset = random.uniform(-radius, radius)

    new_lat = lat + random_lat_offset
    new_lon = lon + random_lon_offset

    # Генерируем случайное количество знаков после запятой (6 или 7) для большего реализма
    precision = random.randint(5, 7)

    # Форматируем строку до нужной точности
    # f-string форматирование - самый современный и удобный способ
    return f"{new_lat:.{precision}f}", f"{new_lon:.{precision}f}"


def _get_location_from_timezone(timezone: str) -> dict:
    # ... (код этой функции не меняется)
    print(f"  [!] ВНИМАНИЕ: Не удалось получить данные по IP. Активирован запасной метод по таймзоне: {timezone}")
    TIMEZONE_TO_CITY_MAP = {
        'America/New_York': {'city': 'New York', 'region': 'New York', 'loc': '40.7128,-74.0060'},
        'Europe/Berlin': {'city': 'Berlin', 'region': 'Berlin', 'loc': '52.5200,13.4050'},
    }
    fallback_data = TIMEZONE_TO_CITY_MAP.get(timezone)
    if fallback_data:
        lat, lon = fallback_data['loc'].split(',')
        # Добавляем реализм даже к запасным данным
        final_lat, final_lon = _add_realism_to_coords(float(lat), float(lon))
        return {
            "latitude": final_lat,
            "longitude": final_lon,
            "city": fallback_data['city'],
            "region": fallback_data['region'],
            "source": "Timezone Fallback"
        }
    return None


def get_approximate_location(device_data: dict) -> dict:
    ip_address = device_data.get('ip')
    expected_timezone = device_data.get('timezone')

    if not ip_address:
        return _get_location_from_timezone(expected_timezone)

    try:
        print(f" -> Запрос геолокации для IP: {ip_address}...")
        response = requests.get(f'https://ipinfo.io/{ip_address}/json', timeout=5)
        response.raise_for_status()

        geo_data = response.json()
        print(" -> Ответ от API получен:")
        pprint(geo_data)

        api_timezone = geo_data.get('timezone')
        if api_timezone and expected_timezone and api_timezone != expected_timezone:
            print(f"\n  [!] ПРЕДУПРЕЖДЕНИЕ: Несоответствие часовых поясов!")
            print(f"      Ожидаемый пояс: {expected_timezone}")
            print(f"      Пояс по IP: {api_timezone}")

        lat_str, lon_str = geo_data.get('loc', '0.0,0.0').split(',')

        # <<< ГЛАВНОЕ ИЗМЕНЕНИЕ ЗДЕСЬ >>>
        # Передаем базовые координаты в функцию для "оживления"
        final_lat, final_lon = _add_realism_to_coords(float(lat_str), float(lon_str))

        return {
            "latitude": final_lat,
            "longitude": final_lon,
            "city": geo_data.get('city'),
            "region": geo_data.get('region'),
            "source": "IP Geolocation (ipinfo.io)"
        }

    except requests.exceptions.RequestException as e:
        print(f"  [!] Ошибка сети при запросе к API: {e}")
        return _get_location_from_timezone(expected_timezone)


location = get_approximate_location(input_data_att)
pprint(location)

