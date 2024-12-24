from flask import Flask, request, jsonify
import pickle
import xgboost
from flask_cors import CORS
from urllib.parse import urlparse
import string
import numpy as np
# Use TensorFlow for Keras model loading
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
import joblib
import random
import requests

model = joblib.load('models\saved_models\model.pkl')


cors = CORS(app, resources={r"/check_url": {"origins": "http://127.0.0.1:5500"}})  # Allow only specific origin


# Feature extraction functions
def abnormal_url(url):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    return int(netloc and netloc in url)

def count_letters(url):
    return sum(char.isalpha() for char in url)

def count_digits(url):
    return sum(char.isdigit() for char in url)

def count_special_chars(url):
    return sum(char in string.punctuation for char in url)

def extract_root_domain(url):
    try:
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc
        parts = netloc.split('.')
        if len(parts) >= 2:
            root_domain = f"{parts[-2]}.{parts[-1]}"
        else:
            root_domain = "0"
    except Exception as e:
        print(f"An error occurred: {e}")
        root_domain = "0"
    return root_domain

def is_http_secure(url):
    return int(urlparse(url).scheme == 'https')

def get_url_region(url):
    ccTLD_to_region = {
         ".ac": "Ascension Island",
        ".ad": "Andorra",
        ".ae": "United Arab Emirates",
        ".af": "Afghanistan",
        ".ag": "Antigua and Barbuda",
        ".ai": "Anguilla",
        ".al": "Albania",
        ".am": "Armenia",
        ".an": "Netherlands Antilles",
        ".ao": "Angola",
        ".aq": "Antarctica",
        ".ar": "Argentina",
        ".as": "American Samoa",
        ".at": "Austria",
        ".au": "Australia",
        ".aw": "Aruba",
        ".ax": "Åland Islands",
        ".az": "Azerbaijan",
        ".ba": "Bosnia and Herzegovina",
        ".bb": "Barbados",
        ".bd": "Bangladesh",
        ".be": "Belgium",
        ".bf": "Burkina Faso",
        ".bg": "Bulgaria",
        ".bh": "Bahrain",
        ".bi": "Burundi",
        ".bj": "Benin",
        ".bm": "Bermuda",
        ".bn": "Brunei Darussalam",
        ".bo": "Bolivia",
        ".br": "Brazil",
        ".bs": "Bahamas",
        ".bt": "Bhutan",
        ".bv": "Bouvet Island",
        ".bw": "Botswana",
        ".by": "Belarus",
        ".bz": "Belize",
        ".ca": "Canada",
        ".cc": "Cocos Islands",
        ".cd": "Democratic Republic of the Congo",
        ".cf": "Central African Republic",
        ".cg": "Republic of the Congo",
        ".ch": "Switzerland",
        ".ci": "Côte d'Ivoire",
        ".ck": "Cook Islands",
        ".cl": "Chile",
        ".cm": "Cameroon",
        ".cn": "China",
        ".co": "Colombia",
        ".cr": "Costa Rica",
        ".cu": "Cuba",
        ".cv": "Cape Verde",
        ".cw": "Curaçao",
        ".cx": "Christmas Island",
        ".cy": "Cyprus",
        ".cz": "Czech Republic",
        ".de": "Germany",
        ".dj": "Djibouti",
        ".dk": "Denmark",
        ".dm": "Dominica",
        ".do": "Dominican Republic",
        ".dz": "Algeria",
        ".ec": "Ecuador",
        ".ee": "Estonia",
        ".eg": "Egypt",
        ".er": "Eritrea",
        ".es": "Spain",
        ".et": "Ethiopia",
        ".eu": "European Union",
        ".fi": "Finland",
        ".fj": "Fiji",
        ".fk": "Falkland Islands",
        ".fm": "Federated States of Micronesia",
        ".fo": "Faroe Islands",
        ".fr": "France",
        ".ga": "Gabon",
        ".gb": "United Kingdom",
        ".gd": "Grenada",
        ".ge": "Georgia",
        ".gf": "French Guiana",
        ".gg": "Guernsey",
        ".gh": "Ghana",
        ".gi": "Gibraltar",
        ".gl": "Greenland",
        ".gm": "Gambia",
        ".gn": "Guinea",
        ".gp": "Guadeloupe",
        ".gq": "Equatorial Guinea",
        ".gr": "Greece",
        ".gs": "South Georgia and the South Sandwich Islands",
        ".gt": "Guatemala",
        ".gu": "Guam",
        ".gw": "Guinea-Bissau",
        ".gy": "Guyana",
        ".hk": "Hong Kong",
        ".hm": "Heard Island and McDonald Islands",
        ".hn": "Honduras",
        ".hr": "Croatia",
        ".ht": "Haiti",
        ".hu": "Hungary",
        ".id": "Indonesia",
        ".ie": "Ireland",
        ".il": "Israel",
        ".im": "Isle of Man",
        ".in": "India",
        ".io": "British Indian Ocean Territory",
        ".iq": "Iraq",
        ".ir": "Iran",
        ".is": "Iceland",
        ".it": "Italy",
        ".je": "Jersey",
        ".jm": "Jamaica",
        ".jo": "Jordan",
        ".jp": "Japan",
        ".ke": "Kenya",
        ".kg": "Kyrgyzstan",
        ".kh": "Cambodia",
        ".ki": "Kiribati",
        ".km": "Comoros",
        ".kn": "Saint Kitts and Nevis",
        ".kp": "Democratic People's Republic of Korea (North Korea)",
        ".kr": "Republic of Korea (South Korea)",
        ".kw": "Kuwait",
        ".ky": "Cayman Islands",
        ".kz": "Kazakhstan",
        ".la": "Laos",
        ".lb": "Lebanon",
        ".lc": "Saint Lucia",
        ".li": "Liechtenstein",
        ".lk": "Sri Lanka",
        ".lr": "Liberia",
        ".ls": "Lesotho",
        ".lt": "Lithuania",
        ".lu": "Luxembourg",
        ".lv": "Latvia",
        ".ly": "Libya",
        ".ma": "Morocco",
        ".mc": "Monaco",
        ".md": "Moldova",
        ".me": "Montenegro",
        ".mf": "Saint Martin (French part)",
        ".mg": "Madagascar",
        ".mh": "Marshall Islands",
        ".mk": "North Macedonia",
        ".ml": "Mali",
        ".mm": "Myanmar",
        ".mn": "Mongolia",
        ".mo": "Macao",
        ".mp": "Northern Mariana Islands",
        ".mq": "Martinique",
        ".mr": "Mauritania",
        ".ms": "Montserrat",
        ".mt": "Malta",
        ".mu": "Mauritius",
        ".mv": "Maldives",
        ".mw": "Malawi",
        ".mx": "Mexico",
        ".my": "Malaysia",
        ".mz": "Mozambique",
        ".na": "Namibia",
        ".nc": "New Caledonia",
        ".ne": "Niger",
        ".nf": "Norfolk Island",
        ".ng": "Nigeria",
        ".ni": "Nicaragua",
        ".nl": "Netherlands",
        ".no": "Norway",
        ".np": "Nepal",
        ".nr": "Nauru",
        ".nu": "Niue",
        ".nz": "New Zealand",
        ".om": "Oman",
        ".pa": "Panama",
        ".pe": "Peru",
        ".pf": "French Polynesia",
        ".pg": "Papua New Guinea",
        ".ph": "Philippines",
        ".pk": "Pakistan",
        ".pl": "Poland",
        ".pm": "Saint Pierre and Miquelon",
        ".pn": "Pitcairn",
        ".pr": "Puerto Rico",
        ".ps": "Palestinian Territory",
        ".pt": "Portugal",
        ".pw": "Palau",
        ".py": "Paraguay",
        ".qa": "Qatar",
        ".re": "Réunion",
        ".ro": "Romania",
        ".rs": "Serbia",
        ".ru": "Russia",
        ".rw": "Rwanda",
        ".sa": "Saudi Arabia",
        ".sb": "Solomon Islands",
        ".sc": "Seychelles",
        ".sd": "Sudan",
        ".se": "Sweden",
        ".sg": "Singapore",
        ".sh": "Saint Helena",
        ".si": "Slovenia",
        ".sj": "Svalbard and Jan Mayen",
        ".sk": "Slovakia",
        ".sl": "Sierra Leone",
        ".sm": "San Marino",
        ".sn": "Senegal",
        ".so": "Somalia",
        ".sr": "Suriname",
        ".ss": "South Sudan",
        ".st": "São Tomé and Príncipe",
        ".sv": "El Salvador",
        ".sx": "Sint Maarten (Dutch part)",
        ".sy": "Syria",
        ".sz": "Eswatini",
        ".tc": "Turks and Caicos Islands",
        ".td": "Chad",
        ".tf": "French Southern Territories",
        ".tg": "Togo",
        ".th": "Thailand",
        ".tj": "Tajikistan",
        ".tk": "Tokelau",
        ".tl": "Timor-Leste",
        ".tm": "Turkmenistan",
        ".tn": "Tunisia",
        ".to": "Tonga",
        ".tr": "Turkey",
        ".tt": "Trinidad and Tobago",
        ".tv": "Tuvalu",
        ".tw": "Taiwan",
        ".tz": "Tanzania",
        ".ua": "Ukraine",
        ".ug": "Uganda",
        ".uk": "United Kingdom",
        ".us": "United States",
        ".uy": "Uruguay",
        ".uz": "Uzbekistan",
        ".va": "Vatican City",
        ".vc": "Saint Vincent and the Grenadines",
        ".ve": "Venezuela",
        ".vg": "British Virgin Islands",
        ".vi": "U.S. Virgin Islands",
        ".vn": "Vietnam",
        ".vu": "Vanuatu",
        ".wf": "Wallis and Futuna",
        ".ws": "Samoa",
        ".ye": "Yemen",
        ".yt": "Mayotte",
        ".za": "South Africa",
        ".zm": "Zambia",
        ".zw": "Zimbabwe"

    }

    root_domain = extract_root_domain(url)
    for tld, region in ccTLD_to_region.items():
        if root_domain.endswith(tld):
            return region

    return "Global"

def hash_encode(value):
    return hash(value) % (1 << 24)

# Preprocessing function
def preprocess_url(url):
    features = []
    features.append(abnormal_url(url))
    features.append(count_letters(url))
    features.append(count_digits(url))
    features.append(count_special_chars(url))
    features.append(is_http_secure(url))

    # Hash the root domain
    root_domain = extract_root_domain(url)
    root_domain_hashed = hash_encode(root_domain)
    features.append(root_domain_hashed)

    # Hash the URL region
    url_region = get_url_region(url)
    url_region_hashed = hash_encode(url_region)
    features.append(url_region_hashed)

    return features

@app.route('/check_url', methods=['POST'])
def check_url():
    print("entered app.py")
    
    # Get the JSON data from the request
    url = request.json['url']  # Adjust according to the structure of the data sent from the frontend

    # Preprocess the URL to extract features
    features = preprocess_url(url)
    print("Extracted features:", features)

    result = model.predict(np.array(features).reshape(1, -1))
    print(result)
        # Check if the URL is malicious
     # Adjust based on your model's input requirements
    print("Prediction result:", result)
    return jsonify({'malicious': int(result[0])})

if __name__ == '__main__':
    app.run(debug=True, port=5000)