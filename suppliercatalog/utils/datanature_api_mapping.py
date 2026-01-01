# -*- coding: utf-8 -*-

"""
Mapping functions for Supplier Catalog import.

All XML inputs are integers (numeric codes). These functions
return the corresponding ERPNext value for each mapping.
"""

# ----------------------------------
# Country of Origin (int -> English name)
# ----------------------------------
def get_country_of_origin(code: int) -> str:
    country_map = {
        18: "Afghanistan", 21: "Egypt", 22: "Aland Islands", 23: "Albania", 24: "Algeria",
        26: "U.S. Virgin Islands", 25: "American Samoa", 27: "Andorra", 28: "Angola",
        29: "Anguilla", 30: "Antarctica", 31: "Antigua and Barbuda", 32: "Equatorial Guinea",
        33: "Argentina", 34: "Armenia", 35: "Aruba", 36: "Ascension", 37: "Azerbaijan",
        38: "Ethiopia", 39: "Australia", 40: "Bahamas", 41: "Bahrain", 42: "Bangladesh",
        43: "Barbados", 44: "Belarus", 46: "Belgium", 47: "Belize", 48: "Benin",
        49: "Bermuda", 50: "Bhutan", 51: "Bolivia", 52: "Bonaire, Sint Eustatius & Saba",
        53: "Bosnia and Herzegovina", 54: "Botswana", 2: "Bouvet Island", 3: "Brazil",
        4: "British Virgin Islands", 5: "British Indian Ocean Territory", 6: "Brunei",
        7: "Bulgaria", 13: "Burkina Faso", 14: "Burundi", 15: "Ceuta & Melilla",
        16: "Chile", 17: "China", 19: "Clipperton Island", 20: "Cook Islands",
        45: "Costa Rica", 55: "Curaçao", 56: "Denmark", 121: "DR Congo", 8: "Germany",
        57: "Diego Garcia", 258: "Various", 58: "Dominica", 59: "Dominican Republic",
        60: "Djibouti", 61: "Ecuador", 62: "El Salvador", 63: "Eritrea", 64: "Estonia",
        66: "European Union", 67: "Falkland Islands", 68: "Faroe Islands", 69: "Fiji",
        70: "Finland", 9: "France", 73: "French Southern Territories", 71: "French Guiana",
        72: "French Polynesia", 74: "Gabon", 75: "Gambia", 76: "Georgia", 77: "Ghana",
        78: "Gibraltar", 79: "Grenada", 80: "Greece", 81: "Greenland", 82: "Guadeloupe",
        83: "Guam", 84: "Guatemala", 85: "Guernsey", 86: "Guinea", 87: "Guinea-Bissau",
        88: "Guyana", 89: "Haiti", 90: "Heard & McDonald Islands", 95: "Honduras",
        96: "Hong Kong", 97: "India", 98: "Indonesia", 99: "Isle of Man", 100: "Iraq",
        101: "Iran", 102: "Ireland", 103: "Iceland", 104: "Israel", 105: "Italy",
        106: "Jamaica", 108: "Japan", 109: "Yemen", 91: "Jersey", 92: "Jordan",
        93: "Cayman Islands", 94: "Cambodia", 107: "Cameroon", 110: "Canada",
        111: "Canary Islands", 112: "Cape Verde", 113: "Kazakhstan", 114: "Qatar",
        115: "Kenya", 116: "Kyrgyzstan", 117: "Kiribati", 118: "Cocos Islands",
        119: "Colombia", 120: "Comoros", 122: "Congo", 126: "Croatia", 127: "Cuba",
        128: "Kuwait", 129: "Laos", 130: "Lesotho", 131: "Latvia", 132: "Lebanon",
        133: "Liberia", 134: "Libya", 135: "Liechtenstein", 136: "Lithuania",
        137: "Luxembourg", 138: "Macau", 139: "Madagascar", 140: "Malawi",
        141: "Malaysia", 142: "Maldives", 143: "Mali", 144: "Malta", 145: "Morocco",
        146: "Marshall Islands", 147: "Martinique", 148: "Mauritania", 149: "Mauritius",
        150: "Mayotte", 151: "North Macedonia", 152: "Mexico", 153: "Micronesia",
        154: "Moldova", 155: "Monaco", 156: "Mongolia", 157: "Montenegro", 158: "Montserrat",
        159: "Mozambique", 160: "Myanmar", 161: "Namibia", 162: "Nauru", 163: "Nepal",
        164: "New Caledonia", 165: "New Zealand", 166: "Nicaragua", 167: "Netherlands",
        168: "Niger", 169: "Nigeria", 170: "Niue", 123: "North Korea", 171: "Northern Mariana Islands",
        172: "Norfolk Island", 173: "Norway", 174: "Oman", 10: "Austria", 176: "Pakistan",
        178: "Palau", 179: "Panama", 180: "Papua New Guinea", 181: "Paraguay",
        182: "Peru", 183: "Philippines", 184: "Pitcairn Islands", 185: "Poland",
        186: "Portugal", 187: "Puerto Rico", 188: "Réunion", 189: "Rwanda", 190: "Romania",
        191: "Russia", 192: "Solomon Islands", 193: "Saint Barthélemy", 194: "Saint Martin (FR)",
        195: "Zambia", 196: "Samoa", 197: "San Marino", 198: "Sao Tome & Principe",
        199: "Saudi Arabia", 200: "Sweden", 201: "Senegal", 202: "Serbia", 203: "Seychelles",
        204: "Sierra Leone", 205: "Zimbabwe", 206: "Singapore", 207: "Sint Maarten (NL)",
        208: "Slovakia", 209: "Slovenia", 210: "Somalia", 212: "Spain", 211: "Sri Lanka",
        177: "State of Palestine", 213: "Saint Kitts & Nevis", 214: "Saint Lucia",
        216: "Saint Vincent & Grenadines", 217: "South Africa", 218: "Sudan",
        219: "South Georgia & South Sandwich Islands", 124: "South Korea", 220: "South Sudan",
        221: "Suriname", 222: "Svalbard & Jan Mayen", 223: "Swaziland", 224: "Syria",
        225: "Tajikistan", 226: "Taiwan", 227: "Tanzania", 228: "Thailand", 229: "Togo",
        230: "Tokelau", 231: "Tonga", 232: "Trinidad & Tobago", 233: "Chad",
        234: "Czech Republic", 235: "Tunisia", 236: "Turkey", 237: "Turkmenistan",
        238: "Turks & Caicos Islands", 239: "Tuvalu", 240: "Uganda", 241: "Ukraine",
        242: "Hungary", 243: "United States Minor Outlying Islands", 244: "Uruguay",
        250: "United States", 245: "Uzbekistan", 246: "Vanuatu", 247: "Vatican City",
        248: "Venezuela", 249: "United Arab Emirates", 251: "United Kingdom",
        252: "Vietnam", 253: "Wallis & Futuna", 254: "Christmas Island", 255: "Western Sahara",
        256: "Central African Republic", 257: "Cyprus"
    }
    return country_map.get(code, None)


# ----------------------------------
# Trade Class (int -> string)
# ----------------------------------
def get_tradeclass(code: int) -> str:
    tradeclass_map = {
        1: "Extra",
        2: "I",
        3: "II",
        4: "No Classification"
    }
    return tradeclass_map.get(code, "Unknown")


# ----------------------------------
# Supplier Quality (int -> abbreviation)
# ----------------------------------
def get_supplier_quality(code: int) -> str:
    supplier_quality_map = {31:"BA",34:"BS",9:"DB",11:"DC",13:"DD",15:"DG",17:"DK",19:"DN",
                            38:"NF",37:"DP",21:"DV",23:"DW",26:"IA",25:"EG",2:"95%",3:"96%",
                            4:"97%",5:"98%",6:"99%",7:"C%",29:"S#",28:"NK",30:"WP",1:"##",
                            33:"UW",27:"NG"}
    return supplier_quality_map.get(code, "Unknown")


# ----------------------------------
# Unit of Measure (content_uom) (int -> name)
# ----------------------------------
def get_content_uom(code: int) -> str:
    content_uom_map = {
        2:"Gramm",4:"Kilogramm",5:"Liter",3:"Meter",6:"Milliliter",
        9:"Paar",11:"Quadratmeter",10:"Quadratzentimeter",1:"Stk",7:"Zentimeter"
    }
    return content_uom_map.get(code, "Unknown")


# ----------------------------------
# Order Unit mapping (int -> name)
# ----------------------------------
def get_order_unit(code: int) -> str:
    orderunit_map = {
        21:"Bag in Box",20:"Banderole",6:"Beutel",14:"Box",10:"Display",15:"Dose",
        8:"Eimer",16:"Fass",1:"Karton",9:"Kasten",2:"Kiste",11:"Korb",12:"Kuvert",
        13:"Netz",7:"Sack",19:"Schrumpffolie",5:"Steige",4:"Stk",17:"Tray (mit Folie)",
        18:"Tray (ohne Folie)"
    }
    return orderunit_map.get(code, "Unknown")


# ----------------------------------
# Shop Unit UOM (int -> name)
# ----------------------------------
def get_shop_unit_uom(code: int) -> str:
    shop_uom_map = {
        51:"Bag in Box",24:"Becher",5:"Beutel",7:"Blatt",25:"Box",9:"Bund",10:"Display",
        26:"Dose",27:"Eimer",28:"Fass",29:"Flasche (Glas)",30:"Flasche (Plastik)",3:"Glas",
        50:"Glasröhrchen",2:"Kanister",49:"Kapsel",6:"Karton",32:"Kasten",53:"No Packaging",
        12:"Kiste",13:"Korb",14:"Kuvert",47:"Laib",15:"Netz",33:"Packung",48:"Pad",
        44:"Riegel",16:"Rolle",46:"Sachet",17:"Sack",34:"Schachtel",18:"Schale",52:"Schraubglas (Plastic)",
        19:"Set",35:"Sixpack",36:"Spender",37:"Stange",38:"Steige",45:"Stick",8:"Stk",
        43:"Tafel",39:"Tiegel",20:"Topf",4:"Tube",41:"Tüte",23:"Verbundkarton",42:"Viererpack",
        21:"Waschladung",22:"Zopf"
    }
    return shop_uom_map.get(code, "Unknown")


# ----------------------------------
# Base Price Unit (int -> name)
# ----------------------------------
def get_base_price_unit(code: int) -> str:
    base_price_map = {
        3:"Kilogramm",7:"Liter",5:"Meter",6:"Quadratmeter",4:"Stk",8:"Waschladung"
    }
    return base_price_map.get(code, "Unknown")


# ----------------------------------
# Tax Amount (price_mwst_id -> percentage)
# ----------------------------------
def get_tax_amount(code: int) -> float:
    # XML pricemwst 1=19%, 2=7%, 3=0%
    tax_map = {1:19.0,2:7.0,3:0.0}
    return tax_map.get(code, 0.0)


# ----------------------------------
# Pfand Type (int -> name)
# ----------------------------------
def get_pfand_type(code: int) -> str:
    pfand_map = {1:"Einweg-Pfand",3:"kein Pfand",2:"Mehrweg-Pfand"}
    return pfand_map.get(code, "Unknown")


# ----------------------------------
# Pfand Amount (int -> value)
# ----------------------------------
def get_pfand_amount(code: int) -> float:
    pfand_amt_map = {1:0.08,2:0.15,3:0.24,4:0.25,5:0.3,6:0.5,7:0.71}
    return pfand_amt_map.get(code, 0.0)


# ----------------------------------
# Pfand Type VPE1 (int -> name)
# ----------------------------------
def get_pfand_type_vpe1(code: int) -> str:
    pfand_vpe1_type_map = {
        5: "Einweg-Pfand",
        4: "kein Pfand",
        1: "Mehrweg-Pfand"
    }
    return pfand_vpe1_type_map.get(code, "Unknown")


# ----------------------------------
# Pfand Amount VPE1 (int -> value)
# ----------------------------------
def get_pfand_amount_vpe1(code: int) -> float:
    pfand_vpe1_map = {1:1.25,2:1.5,3:2.5,4:3.0,5:3.5,6:4.0}
    return pfand_vpe1_map.get(code, 0.0)

# ----------------------------------
# List of Ingredients Legend (int -> name)
# ----------------------------------
def get_ingredients_legend(code: int) -> str:
    ingredients_legend_map = {
        1:"*aus kontrolliert ökologischer Erzeugung",
        2:"**aus biodynamischem Erzeugung",
        3:"***aus anerkannt ökologischer Aquakultur",
        4:"****aus Wildfang",
        7:"*****aus bio-zertifizierter Wildsammlung",
        5:"keine Zutatenlegende (100% konventionelle Zutaten)"
    }
    return ingredients_legend_map.get(code, "")