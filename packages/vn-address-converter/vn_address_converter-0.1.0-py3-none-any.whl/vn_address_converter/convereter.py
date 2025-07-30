import json
import os
import re
import unicodedata
from typing import TypedDict
from enum import Enum

# Address TypedDict represents a Vietnamese address with optional fields.
class Address(TypedDict):
    street_address: str | None  # Street address (optional)
    ward: str | None           # Ward/commune name (optional)
    district: str | None       # District name (optional)
    province: str | None       # Province/city name (optional)

class AddressLevel(Enum):
    PROVINCE = 'province'
    DISTRICT = 'district'
    WARD = 'ward'

WARD_MAPPING_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ward_mapping.json')
WARD_MAPPING = None

def normalize_alias(name: str, level: 'AddressLevel') -> str:
    if level == AddressLevel.PROVINCE:
        remove_words = ['thành phố', 'tỉnh']
    elif level == AddressLevel.DISTRICT:
        remove_words = ['thành phố', 'quận', 'huyện']
    elif level == AddressLevel.WARD:
        remove_words = ['phường', 'xã']
    else:
        remove_words = []
    name = unicodedata.normalize("NFC", name)
    pattern = r"^(%s)\s*" % "|".join([re.escape(w) for w in remove_words])  # <-- FIXED: single backslash
    name = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
    return name.lower()

def _get_ward_mapping():
    global WARD_MAPPING
    if WARD_MAPPING is None:
        with open(WARD_MAPPING_PATH, encoding='utf-8') as f:
            mapping = json.load(f)
        province_aliases = {}
        district_aliases = {}
        ward_aliases = {}
        for prov_name, prov_val in mapping.items():
            prov_alias = normalize_alias(prov_name, AddressLevel.PROVINCE)
            # Always add normalized alias (if not empty) and lowercased original name
            if prov_alias:
                province_aliases[prov_alias] = prov_name
            province_aliases[prov_name.lower()] = prov_name
            district_aliases[prov_name] = {}
            ward_aliases[prov_name] = {}
            for dist_name, dist_val in prov_val.items():
                dist_alias = normalize_alias(dist_name, AddressLevel.DISTRICT)
                district_aliases[prov_name][dist_alias] = dist_name
                district_aliases[prov_name][dist_name.lower()] = dist_name
                ward_aliases[prov_name][dist_name] = {}
                for ward_name in dist_val:
                    ward_alias = normalize_alias(ward_name, AddressLevel.WARD)
                    ward_aliases[prov_name][dist_name][ward_alias] = ward_name
                    ward_aliases[prov_name][dist_name][ward_name.lower()] = ward_name
        WARD_MAPPING = {
            'mapping': mapping,
            'province_aliases': province_aliases,
            'district_aliases': district_aliases,
            'ward_aliases': ward_aliases
        }
    return WARD_MAPPING

def convert_to_new_address(address: Address) -> Address:
    province = address.get('province')
    district = address.get('district')
    ward = address.get('ward')
    street_address = address.get('street_address')

    if not province or not district or not ward:
        raise ValueError('Missing province, district, or ward in address')

    mapping_obj = _get_ward_mapping()
    mapping = mapping_obj['mapping']
    province_aliases = mapping_obj['province_aliases']
    district_aliases = mapping_obj['district_aliases']
    ward_aliases = mapping_obj['ward_aliases']

    province_norm = normalize_alias(province, AddressLevel.PROVINCE)
    province_key = province if province in mapping else province_aliases.get(province_norm)
    if not province_key or province_key not in mapping:
        raise ValueError(f'Province not found in mapping: {province}')
    province_map = mapping[province_key]

    district_norm = normalize_alias(district, AddressLevel.DISTRICT)
    district_key = district if district in province_map else district_aliases[province_key].get(district_norm)
    if not district_key or district_key not in province_map:
        raise ValueError(f'District not found in mapping: {district}')
    district_map = province_map[district_key]

    ward_norm = normalize_alias(ward, AddressLevel.WARD)
    ward_key = ward if ward in district_map else ward_aliases[province_key][district_key].get(ward_norm)
    if not ward_key or ward_key not in district_map:
        raise ValueError(f'Ward not found in mapping: {ward}')
    ward_map = district_map[ward_key]

    new_province = ward_map['new_provine_name']
    new_ward = ward_map['new_ward_name']

    return Address(
        street_address=street_address,
        ward=new_ward,
        district=None,
        province=new_province
    )
