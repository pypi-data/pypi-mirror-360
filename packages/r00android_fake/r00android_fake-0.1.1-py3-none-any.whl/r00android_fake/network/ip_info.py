import random
import re

import httpx

from r00arango_connector import connect_arango
from r00logger import log

DEBUG = False

# Минимальная длина бренда/ключевого слова для участия в интеллектуальном поиске.
MIN_KEYWORD_LENGTH = 3

DB_NAME = "android"
COLLECTION_NAME = "countries"

# "Мусорные" слова, которые нужно игнорировать при поиске по названию организации
OPERATOR_NAME_STOP_WORDS = {
    'llc', 'inc', 'pjsc', 'gmbh', 'ltd', 'sa', 'ag', 'communications',
    'telecom', 'mobile', 's.a.', 'o.o.', 'the', 'cjsc'
}

# Сопоставление кодов стран с их мобильными кодами (MCC) для определения "родных" сетей
COUNTRY_TO_MCC = {"BG": ["284"], "SN": ["608", "610"], "TR": ["286"],
                  "AE": ["641", "640", "639", "636", "634", "424", "419", "422", "426", "427"],
                  "ZA": ["655", "643", "645", "651", "652", "649", "617"], "IL": ["425", "208"],
                  "CH": ["228", "295", "206"], "BR": ["724"], "TN": ["605"], "UA": ["255", "259"], "IR": ["432"],
                  "AT": ["232", "206"], "UZ": ["434", "437", "436", "428", "438"], "HU": ["216", "206"],
                  "VN": ["452"], "GH": ["620", "624", "612"], "IN": ["405", "406", "404"], "KR": ["450"],
                  "MA": ["604"], "DE": ["262"], "PL": ["260"], "LU": ["206", "270"], "CZ": ["230"],
                  "RS": ["297", "293", "220", "218", "294", "219", "276", "214"],
                  "RU": ["250", "240", "257", "400", "282", "283"],
                  "PA": ["712", "714", "704", "706", "708", "710", "330"], "PH": ["515"], "RO": ["226"],
                  "GR": ["202", "280"], "AF": ["412"], "LV": ["247", "246", "248"],
                  "FR": ["208", "647", "212", "206", "340"], "GB": ["234", "240", "206", "272"], "EC": ["740"],
                  "TW": ["466", "525"], "CL": ["730", "736"], "AR": ["722"], "SA": ["420"], "CO": ["732"],
                  "US": ["001", "310", "311", "999", "313", "312", "204", "262", "234", "214", "246"],
                  "PT": ["268"], "PK": ["410"], "CA": ["302", "204", "206"], "NP": ["429"], "BD": ["470"],
                  "NL": ["204", "240"], "MY": ["502"], "IT": ["222", "228", "208"],
                  "TT": ["374", "370", "365", "344", "342", "348", "346", "366", "352", "338", "354", "356", "358",
                         "360", "376", "364"], "KZ": ["401"], "LK": ["413", "472"], "SG": ["525", "528"],
                  "TH": ["456", "457", "414", "520"], "NG": ["621", "618"], "EG": ["602"], "ES": ["214", "213"],
                  "GE": ["250", "240", "257", "400", "282", "283"],
                  "SE": ["901", "244", "240", "242", "238", "274", "290", "222", "288"], "IQ": ["416", "425"],
                  "SK": ["231"]}


def get_countries_to_mcc():
    db = connect_arango('android')
    res = db.aql.execute("""
        RETURN MERGE(
        FOR country IN countries
            LET all_mccs_for_country = FLATTEN(
                FOR csc_region IN VALUES(country.csc)
                    FILTER HAS(csc_region, "networks")
                    RETURN (
                        FOR network IN VALUES(csc_region.networks)
                            FILTER HAS(network, "mcc")
                            RETURN network.mcc
                    )
            )
            LET unique_mccs = UNIQUE(all_mccs_for_country)
            RETURN { [country._key] : unique_mccs }
    )
        """)
    return res.next()


def get_full_ip_info(proxy_host: str = None, proxy_port: int = None) -> dict:
    proxy_url = None
    if proxy_host and proxy_port:
        proxy_url = f'socks5h://{proxy_host}:{proxy_port}'

    try:
        with httpx.Client(proxy=proxy_url, timeout=15) as client:
            response = client.get('https://ipinfo.io/json')
            response.raise_for_status()
            return response.json()
    except Exception as e:
        log.exception(f"Ошибка при получении данных об IP через прокси {proxy_url}", e)
        raise


def is_network_data_poor(network_data: dict) -> bool:
    """Проверяет сеть на "пустые" или некачественные данные (устойчива к None)."""
    null_values = {None, 'n/a', 'unknown'}
    brand = network_data.get('brand')
    operator_full = network_data.get('operator_full')
    bands = network_data.get('bands')

    is_brand_poor = brand is None or (isinstance(brand, str) and brand.lower() in null_values)
    is_operator_poor = operator_full is None or (
            isinstance(operator_full, str) and operator_full.lower() in null_values)
    is_bands_poor = bands is None or (isinstance(bands, str) and bands.lower() in null_values)

    return is_brand_poor or is_operator_poor or is_bands_poor


def score_network(network: dict, native_mccs: list[str]) -> int:
    """
    Оценивает сеть по качеству и "родному" происхождению.
    Возвращает: 2 (родная, качественная), 1 (не родная, качественная), 0 (плохие данные).
    """
    if is_network_data_poor(network):
        return 0
    if network.get('mcc') in native_mccs:
        return 2
    return 1


def build_final_config(country_doc: dict, csc_code: str, network: dict) -> dict:
    """Собирает финальный словарь с конфигурацией."""
    csc_data = country_doc['csc'][csc_code]
    return {
        'mcc': network.get('mcc'), 'mnc': network.get('mnc'),
        'network_name': network.get('network_name'), 'brand': network.get('brand'),
        'operator_full': network.get('operator_full'), 'csc': csc_code,
        # 'default_language': csc_data.get('default_language'),
        # 'CscFeature_RIL_ConfigNetworkTypeCapability': csc_data.get('CscFeature_RIL_ConfigNetworkTypeCapability'),
        'country_code': country_doc.get('_key'), 'phone_code': country_doc.get('phone_code'),
    }


def get_intelligent_config(ip_info: dict, country_doc: dict) -> dict | None:
    """Основная функция для интеллектуального подбора полной конфигурации."""
    org_name = ip_info.get('org', '').lower()
    country_code = country_doc.get('_key')
    all_csc_data = country_doc.get('csc', {})
    native_mccs = COUNTRY_TO_MCC.get(country_code, [])

    print(f"[*] Анализирую организацию: '{org_name}' для страны '{country_code}' (родные MCC: {native_mccs}).")

    # Шаг 1: Улучшенный сбор ключевых слов
    searchable_keywords = set()
    for csc_data in all_csc_data.values():
        for network in csc_data.get('networks', {}).values():
            for text_source in [network.get('brand'), network.get('operator_full')]:
                if not text_source or not isinstance(text_source, str):
                    continue

                cleaned_text = text_source.lower()
                for stop_word in OPERATOR_NAME_STOP_WORDS:
                    cleaned_text = cleaned_text.replace(stop_word, ' ')
                cleaned_text = re.sub(r'[^a-z0-9\s]', '', cleaned_text).strip()

                # Добавляем как цельные названия, так и отдельные слова
                if cleaned_text and len(re.sub(r'\s', '', cleaned_text)) >= MIN_KEYWORD_LENGTH:
                    searchable_keywords.add(cleaned_text)
                    for word in cleaned_text.split():
                        if len(word) >= MIN_KEYWORD_LENGTH:
                            searchable_keywords.add(word)

    if DEBUG: print(f"[DEBUG] Сформирован список ключевых слов для поиска: {sorted(list(searchable_keywords))}")

    # Шаг 2: Надежный поиск
    cleaned_org_name = ' ' + re.sub(r'[^a-z0-9\s]', '', org_name) + ' '
    found_keywords = {kw for kw in searchable_keywords if f' {kw} ' in cleaned_org_name}

    chosen_candidate = None
    if found_keywords:
        print(f"[+] Найдены потенциальные ключевые слова: {list(found_keywords)}")
        candidates = []
        for csc_code, csc_data in all_csc_data.items():
            for network in csc_data.get('networks', {}).values():
                net_text = f"{(network.get('brand') or '')} {(network.get('operator_full') or '')}".lower()
                if any(kw in net_text for kw in found_keywords):
                    score = score_network(network, native_mccs)
                    candidates.append({'csc': csc_code, 'network': network, 'score': score})

        if candidates:
            candidates.sort(key=lambda x: x['score'], reverse=True)
            best_score = candidates[0]['score']
            if best_score > 0:
                best_candidates = [c for c in candidates if c['score'] == best_score]
                chosen_candidate = random.choice(best_candidates)
                print(
                    f"[+] Интеллектуально выбран CSC '{chosen_candidate['csc']}' и сеть '{chosen_candidate['network'].get('network_name')}' (качество: {best_score}/2)")

    # Шаг 3: Fallback, если интеллектуальный выбор не удался
    if not chosen_candidate:
        print(f"[!] Не найдено прямого совпадения. Включаю улучшенный fallback-механизм.")
        candidates = []
        for csc_code, csc_data in all_csc_data.items():
            for network in csc_data.get('networks', {}).values():
                score = score_network(network, native_mccs)
                candidates.append({'csc': csc_code, 'network': network, 'score': score})

        if not candidates:
            print("[!] Не удалось найти сетей для fallback.")
            return None

        candidates.sort(key=lambda x: x['score'], reverse=True)
        best_score = candidates[0]['score']
        best_candidates = [c for c in candidates if c['score'] == best_score]
        chosen_candidate = random.choice(best_candidates)
        print(
            f"[+] Случайно выбран (по приоритету) CSC '{chosen_candidate['csc']}' и сеть '{chosen_candidate['network'].get('network_name')}' (качество: {best_score}/2)")

    return build_final_config(country_doc, chosen_candidate['csc'], chosen_candidate['network'])


def get_network_configuration_by_home():
    return _get_network_configuration()


def get_network_configuration_by_manual(data_ipinfo: dict):
    return _get_network_configuration(data_ipinfo=data_ipinfo)


def get_network_configuration_by_proxy(proxy_ip, proxy_port):
    return _get_network_configuration(proxy_ip=proxy_ip, proxy_port=proxy_port)


def _get_network_configuration(**kwargs):
    proxy_ip = kwargs.get('proxy_ip')
    proxy_port = kwargs.get('proxy_port')
    data_ipinfo = kwargs.get('data_ipinfo')

    if proxy_ip and proxy_port:
        ip_information = get_full_ip_info(proxy_ip, proxy_port)
    elif data_ipinfo:
        ip_information = data_ipinfo
    else:
        ip_information = get_full_ip_info()

    if ip_information and ip_information.get('country'):
        country_code = ip_information.get('country')
        try:
            db = connect_arango(DB_NAME)
            country_document = db.collection(COLLECTION_NAME).get(country_code)
            if country_document:
                final_config = get_intelligent_config(ip_information, country_document)
                if final_config:
                    final_config.update({
                        'ip': ip_information.get('ip'),
                        'city': ip_information.get('city'),
                        'region': ip_information.get('region'),
                        'loc': ip_information.get('loc'),
                        'timezone': ip_information.get('timezone')
                    })
                    return final_config
                else:
                    log.error('final_config is empty')
            else:
                print(f"[!] Документ для страны '{country_code}' не найден в базе данных.")
        except Exception as e:
            print(f"[!] Ошибка при работе с ArangoDB: {e}")

# {"ip": "85.140.5.132", "hostname": "132.mtsnet.ru", "city": "Ufa", "region": "Bashkortostan Republic", "country": "RU", "loc": "54.7431,55.9678", "org": "AS8359 MTS PJSC", "postal": "450511", "timezone": "Asia/Yekaterinburg", "readme": "https://ipinfo.io/missingauth" }
