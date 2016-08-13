"""Module for generating countries and region lists.

This module has all the helper functions for generating proper structures for
CountryTreeWidget.

The three main exposed functions are:
    get_countries_dict - Used in climate widget.
    get_countries_regions_dict - Used in indicator widget.
    get_alpha3_map - used for changing alpha3 codes to country names.
"""
import copy
import logging
from collections import defaultdict
from collections import OrderedDict

import pycountry
import simple_wbd

logger = logging.getLogger(__name__)

MAPPINGS = {
    # Africa
    "Democratic Republic of the Congo": ("Congo, The Democratic Republic of "
                                         "the"),
    "Ivory Coast": "Côte d'Ivoire",
    "Tanzania": "Tanzania, United Republic of",
    "Iran": "Iran, Islamic Republic of",

    # Asia
    "Macau": "Macao",
    "Northern Cyprus": "Cyprus",
    "South Korea": "Korea, Republic of",
    "North Korea": "Korea, Democratic People's Republic of",
    "Vietnam": "Viet Nam",
    "Palestine": "Palestine, State of",
    "Taiwan": "Taiwan, Province of China",
    "Syria": "Syrian Arab Republic",

    # Europe
    "Macedonia": "Macedonia, Republic of",
    "Moldova": "Moldova, Republic of",
    "Russia": "Russian Federation",
    "Vatican City/Holy See": "Holy See (Vatican City State)",

    # North America
    "Bonaire": "Bonaire, Sint Eustatius and Saba",
    "British Virgin Islands": "Virgin Islands, British",
    "Saint Martin": "Saint Martin (French part)",
    "Sint Maarten": "Sint Maarten (Dutch part)",
    "United States of America": "United States",
    "United States Virgin Islands": "Virgin Islands, U.S.",

    # South America
    "Bolivia": "Bolivia, Plurinational State of",
    "Falkland Islands": "Falkland Islands (Malvinas)",
    "Venezuela": "Venezuela, Bolivarian Republic of",

    # Oceania
    "Pitcairn Islands": "Pitcairn",
    "Micronesia": "Micronesia, Federated States of",

    # Antartica
    "French Southern and Antarctic Lands": "French Southern Territories",
}

COUNTRIES = {
    "Africa": [
        "Algeria",
        "Angola",
        "Benin",
        "Botswana",
        "Burkina Faso",
        "Burundi",
        "Cameroon",
        "Cape Verde",
        "Central African Republic",
        "Chad",
        "Comoros",
        "Congo",
        "Democratic Republic of the Congo",
        "Djibouti",
        "Egypt",
        "Equatorial Guinea",
        "Eritrea",
        "Ethiopia",
        "Gabon",
        "Gambia",
        "Ghana",
        "Guinea",
        "Guinea-Bissau",
        "Ivory Coast",
        "Kenya",
        "Lesotho",
        "Liberia",
        "Libya",
        "Madagascar",
        "Malawi",
        "Mali",
        "Mauritania",
        "Mauritius",
        "Mayotte",
        "Morocco",
        "Mozambique",
        "Namibia",
        "Niger",
        "Nigeria",
        "Réunion",
        "Rwanda",
        # "Sahrawi Arab Democratic Republic",
        "Saint Helena, Ascension and Tristan da Cunha",
        # "São Tomé and Príncipe",
        "Senegal",
        "Seychelles",
        "Sierra Leone",
        "Somalia",
        # "Somaliland",
        "South Africa",
        "South Sudan",
        "Sudan",
        "Swaziland",
        "Tanzania",
        "Togo",
        "Tunisia",
        "Uganda",
        "Zambia",
        "Zimbabwe",
    ],
    "Asia": [
        "China",
        "Christmas Island",
        "Hong Kong",
        "India",
        "Indonesia",
        "Iran",
        "Iraq",
        "Israel",
        "Japan",
        "Jordan",
        "Kazakhstan",
        "Kuwait",
        "Kyrgyzstan",
        # "Laos",
        "Lebanon",
        "Macau",
        "Malaysia",
        "Maldives",
        "Mongolia",
        "Myanmar",
        # "Nagorno-Karabakh",
        "Nepal",
        "Northern Cyprus",
        "North Korea",
        "Oman",
        "Pakistan",
        "Palestine",
        "Philippines",
        "Qatar",
        "Saudi Arabia",
        "Singapore",
        "South Korea",
        # "South Ossetia",
        "Sri Lanka",
        "Syria",
        "Taiwan",
        "Tajikistan",
        "Thailand",
        "Turkey",
        "Turkmenistan",
        "United Arab Emirates",
        "Uzbekistan",
        "Vietnam",
        "Yemen",
    ],
    "Europe": [
        "Åland Islands",
        "Albania",
        "Andorra",
        "Austria",
        "Belarus",
        "Belgium",
        "Bosnia and Herzegovina",
        "Bulgaria",
        "Croatia",
        "Czech Republic",
        "Denmark",
        "Estonia",
        "Faroe Islands",
        "Finland",
        "France",
        "Germany",
        "Gibraltar",
        "Greece",
        "Guernsey",
        "Hungary",
        "Iceland",
        "Ireland",
        "Isle of Man",
        "Italy",
        # "Jan Mayen",  # see Svalbard
        "Jersey",
        # "Kosovo",
        "Latvia",
        "Liechtenstein",
        "Lithuania",
        "Luxembourg",
        "Macedonia",
        "Malta",
        "Moldova",
        "Monaco",
        "Montenegro",
        "Netherlands",
        "Norway",
        "Poland",
        "Portugal",
        "Romania",
        "Russia",
        "San Marino",
        "Serbia",
        "Slovakia",
        "Slovenia",
        "Spain",
        # "Svalbard",
        "Svalbard and Jan Mayen",
        "Sweden",
        "Switzerland",
        # "Transnistria",
        "Ukraine",
        "United Kingdom",
        "Vatican City/Holy See",
    ],
    "NorthAmerica": [
        "Anguilla",
        "Antigua and Barbuda",
        "Aruba",
        "Bahamas",
        "Barbados",
        "Belize",
        "Bermuda",
        "Bonaire",
        "British Virgin Islands",
        "Canada",
        "Cayman Islands",
        # "Clipperton Island",
        "Costa Rica",
        "Cuba",
        "Curaçao",
        "Dominica",
        "Dominican Republic",
        "El Salvador",
        "Greenland",
        "Grenada",
        "Guadeloupe",
        "Guatemala",
        "Haiti",
        "Honduras",
        "Jamaica",
        "Martinique",
        "Mexico",
        "Montserrat",
        # "Navassa Island",
        "Nicaragua",
        "Panama",
        "Puerto Rico",
        # "Saba",
        "Saint Barthélemy",
        "Saint Kitts and Nevis",
        "Saint Lucia",
        "Saint Martin",
        "Saint Pierre and Miquelon",
        "Saint Vincent and the Grenadines",
        # "Sint Eustatius",
        "Sint Maarten",
        "Trinidad and Tobago",
        "Turks and Caicos Islands",
        "United States of America",
        "United States Virgin Islands",
    ],
    "SouthAmerica": [
        "Argentina",
        "Bolivia",
        "Brazil",
        "Chile",
        "Colombia",
        "Ecuador",
        "Falkland Islands",
        "French Guiana",
        "Guyana",
        "Paraguay",
        "Peru",
        "South Georgia and the South Sandwich Islands",
        "Suriname",
        "Uruguay",
        "Venezuela",
    ],
    "Oceania": [
        "American Samoa",
        # "Ashmore and Cartier Islands",
        "Australia",
        # "Baker Island",
        "Cook Islands",
        # "Coral Sea Islands",
        "Fiji",
        "French Polynesia",
        "Guam",
        # "Howland Island",
        # "Jarvis Island",
        # "Johnston Atoll",
        # "Kingman Reef",
        "Kiribati",
        "Marshall Islands",
        "Micronesia",
        # "Midway Atoll",
        "Nauru",
        "New Caledonia",
        "New Zealand",
        "Niue",
        "Norfolk Island",
        "Northern Mariana Islands",
        "Palau",
        # "Palmyra Atoll",
        "Papua New Guinea",
        "Pitcairn Islands",
        "Samoa",
        "Solomon Islands",
        "Tokelau",
        "Tonga",
        "Tuvalu",
        "Vanuatu",
        # "Wake Island",
        "Wallis and Futuna",
    ],
    "Antartica": [
        "Bouvet Island",
        "French Southern and Antarctic Lands",
        "Heard Island and McDonald Islands",
        "South Georgia and the South Sandwich Islands",
    ],
}

DATA_STRUCTURE = [
    ("Aggregates", [
        ("Income Levels", [
            "LIC",  # "Low income"
            "MIC",  # "Middle income",
            "LMC",  # "Lower middle income",
            "UMC",  # "Upper middle income",
            "HIC",  # "High income",
        ]),
        ("Regions", [
            "EAS",  # "East Asia & Pacific (all income levels)",
            "ECS",  # "Europe & Central Asia (all income levels)",
            "LCN",  # "Latin America & Caribbean (all income levels)",
            "MEA",  # "Middle East & North Africa (all income levels)",
            "NAC",  # "North America",
            "SAS",  # "South Asia",
            "SSF",  # "Sub-Saharan Africa (all income levels)",
        ]),
        ("Other", [
            "WLD",  # "World",
            "AFR",  # "Africa",
            "ARB",  # "Arab World",
            ("Low & middle income", [
                "LMY",  # "All low and middle income regions",
                "EAP",  # "East Asia & Pacific (developing only)",
                "ECA",  # "Europe & Central Asia (developing only)",
                "LAC",  # "Latin America & Caribbean (developing only)",
                "MNA",  # "Middle East & North Africa (developing only)",
                "SSA",  # "Sub-Saharan Africa (developing only)",
            ]),
            "EMU",  # other high income areas don't exist anymore
            # ("High income", [
            #     "EMU",  # "Euro area",
            #     "OEC",  # "High income: OECD",
            #     "NOC",  # "High income: nonOECD",
            # ]),
            "CEB",  # "Central Europe and the Baltics",
            "EUU",  # "European Union",
            "FCS",  # "Fragile and conflict affected situations",
            "HPC",  # "Heavily indebted poor countries (HIPC)",
            "IBD",  # "IBRD only",
            "IBT",  # "IDA & IBRD total",
            "IDB",  # "IDA blend",
            "IDX",  # "IDA only",
            "IDA",  # "IDA total",
            "LDC",  # "Least developed countries: UN classification",
            "OED",  # "OECD members",
            ("Small states", [
                "SST",  # "All small states",
                "CSS",  # "Caribbean small states",
                "PSS",  # "Pacific island small states",
                "OSS",  # "Other small states",
            ]),
        ]),
    ]),
    ("Countries", []),
]

RENAME_MAP = {
    "SST": "All small states",
    "EMU": "High Income Euro area",
}


def _order_countries_dict(countries):
    return OrderedDict(sorted(countries.items(), key=lambda x: x[1]["name"]))


def get_alpha3_map():
    """Get mappings from alpha3 codes to country names."""
    name_map = {v: k for k, v in MAPPINGS.items()}
    return {c.alpha3: name_map.get(c.name, c.name)
            for c in pycountry.countries}


def get_countries_dict():
    """Get a dict of all all country codes and names grouped by continent."""
    result = defaultdict(dict)
    alpha_map = {c.name: c.alpha3 for c in pycountry.countries}
    for continent, countries in COUNTRIES.items():
        for country in countries:
            result[continent][alpha_map[MAPPINGS.get(country, country)]] = {
                "name": country
            }
    result = {k: _order_countries_dict(v) for k, v in result.items()}
    ordered_result = OrderedDict(sorted(result.items(), key=lambda t: t[0]))
    return ordered_result


def _gather_used_ids(items):
    ids = set()
    for item in items:
        if isinstance(item, str):
            ids.add(item)
        else:
            ids |= _gather_used_ids(item[1])
    return ids


def _add_missing_aggregates(data):
    """Add any missing aggregates to data.

    The data structure might be missing any newly added aggregates from the
    API. This function will add all of those under the other section of
    aggregates list.
    """
    api = simple_wbd.IndicatorAPI()
    countries = api.get_countries()
    aggregate_codes = set(
        [i.get("id") for i in countries if
         i.get("region", {}).get("value") == "Aggregates"]
    )
    used_codes = _gather_used_ids(data)
    missing_aggregates = aggregate_codes.difference(used_codes)
    for code in sorted(missing_aggregates):
        # 0,1 = Aggregates, 2,1 = Other
        data[0][1][2][1].append(code)
    return data


def _add_missing_countries(data):
    """Add all countries from the API to country data."""
    api = simple_wbd.IndicatorAPI()
    countries = api.get_countries()
    country_codes = set(
        [i.get("id") for i in countries if
         i.get("region", {}).get("value") != "Aggregates"]
    )
    for code in sorted(country_codes):
        # 1,1 = Countries
        data[1][1].append(code)
    return data


def _generate_country_map():
    api = simple_wbd.IndicatorAPI()
    countries = api.get_countries()
    return {c["id"]: c for c in countries}


def _generate_country_dict(data):
    """Turn the country and region structure into an ordered dict."""
    country_map = _generate_country_map()
    country_dict = OrderedDict()

    for item in data:
        if isinstance(item, tuple):
            country_dict[item[0]] = _generate_country_dict(item[1])
        elif item in country_map:
            country_dict[item] = country_map[item]
        else:
            logger.info("Missing country item: %s", item)
    return country_dict


def get_countries_regions_dict():
    """Get country and region data for indicators widget."""
    data = copy.deepcopy(DATA_STRUCTURE)
    data = _add_missing_aggregates(data)
    data = _add_missing_countries(data)
    return _generate_country_dict(data)
