import Orange
import numpy

data = numpy.array([
  ["a", 5, 1],
  ["b", 5, 3],
  ["c", 5, 4],
  ["a", 5, None],
  ["c", 5, 4],
])

country = Orange.data.StringVariable("country")
t = Orange.data.TimeVariable("T")
val  = Orange.data.ContinuousVariable("stuff")

domain = Orange.data.domain.Domain([val], metas=[country, t])
table = Orange.data.Table(domain, data[:,2:], metas=data[:,:2])
print(table)


import simple_wbd

api = simple_wbd.IndicatorAPI()

ds = api.get_dataset("SP.POP.TOTL", countries=["US", "SI"])

print(ds.as_list(time_series=True))





AFRICA (54)

    Algeria
    Angola
    Benin
    Botswana
    Burkina
    Burundi
    Cameroon
    Cape Verde
    Central African Republic
    Chad
    Comoros
    Congo
    Congo, Democratic Republic of
    Djibouti
    Egypt
    Equatorial Guinea
    Eritrea
    Ethiopia
    Gabon
    Gambia
    Ghana
    Guinea
    Guinea-Bissau
    Ivory Coast
    Kenya
    Lesotho
    Liberia
    Libya
    Madagascar
    Malawi
    Mali
    Mauritania
    Mauritius
    Morocco
    Mozambique
    Namibia
    Niger
    Nigeria
    Rwanda
    Sao Tome and Principe
    Senegal
    Seychelles
    Sierra Leone
    Somalia
    South Africa
    South Sudan
    Sudan
    Swaziland
    Tanzania
    Togo
    Tunisia
    Uganda
    Zambia
    Zimbabwe

ASIA (44)

    Afghanistan
    Bahrain
    Bangladesh
    Bhutan
    Brunei
    Burma (Myanmar)
    Cambodia
    China
    East Timor
    India
    Indonesia
    Iran
    Iraq
    Israel
    Japan
    Jordan
    Kazakhstan
    Korea, North
    Korea, South
    Kuwait
    Kyrgyzstan
    Laos
    Lebanon
    Malaysia
    Maldives
    Mongolia
    Nepal
    Oman
    Pakistan
    Philippines
    Qatar
    Russian Federation
    Saudi Arabia
    Singapore
    Sri Lanka
    Syria
    Tajikistan
    Thailand
    Turkey
    Turkmenistan
    United Arab Emirates
    Uzbekistan
    Vietnam
    Yemen

EUROPE (47)

    Albania
    Andorra
    Armenia
    Austria
    Azerbaijan
    Belarus
    Belgium
    Bosnia and Herzegovina
    Bulgaria
    Croatia
    Cyprus
    Czech Republic
    Denmark
    Estonia
    Finland
    France
    Georgia
    Germany
    Greece
    Hungary
    Iceland
    Ireland
    Italy
    Latvia
    Liechtenstein
    Lithuania
    Luxembourg
    Macedonia
    Malta
    Moldova
    Monaco
    Montenegro
    Netherlands
    Norway
    Poland
    Portugal
    Romania
    San Marino
    Serbia
    Slovakia
    Slovenia
    Spain
    Sweden
    Switzerland
    Ukraine
    United Kingdom
    Vatican City

N. AMERICA (23)

    Antigua and Barbuda
    Bahamas
    Barbados
    Belize
    Canada
    Costa Rica
    Cuba
    Dominica
    Dominican Republic
    El Salvador
    Grenada
    Guatemala
    Haiti
    Honduras
    Jamaica
    Mexico
    Nicaragua
    Panama
    Saint Kitts and Nevis
    Saint Lucia
    Saint Vincent and the Grenadines
    Trinidad and Tobago
    United States

OCEANIA (14)

    Australia
    Fiji
    Kiribati
    Marshall Islands
    Micronesia
    Nauru
    New Zealand
    Palau
    Papua New Guinea
    Samoa
    Solomon Islands
    Tonga
    Tuvalu
    Vanuatu

S. AMERICA (12)

    Argentina
    Bolivia
    Brazil
    Chile
    Colombia
    Ecuador
    Guyana
    Paraguay
    Peru
    Suriname
    Uruguay
    Venezuela

