"""
Crowseek Prospector — OpenStreetMap Edition
-------------------------------------------

Installation :
    pip install requests

Usage :
    python prospector_osm.py
"""

import requests
import csv
import time
from datetime import datetime


CATEGORIES = [
    ("amenity", "restaurant"),
    ("amenity", "cafe"),
    ("amenity", "fast_food"),
    ("amenity", "bar"),
    ("shop",    "hairdresser"),
    ("shop",    "bakery"),
    ("shop",    "florist"),
    ("shop",    "butcher"),
    ("shop",    "optician"),
    ("amenity", "dentist"),
    ("amenity", "veterinary"),
    ("shop",    "car_repair"),
    ("amenity", "pharmacy"),
]

# Villes cibles — ajoute autant que tu veux
# Format : "Nom de la ville" : (latitude, longitude)
# Pour trouver les coordonnées d'une ville : https://www.latlong.net
CITIES = {
    "Clermont-Ferrand" : (45.7772,  3.0870),
    "Vichy"            : (46.1281,  3.4265),
    "Riom"             : (45.8942,  3.1133),
    "Issoire"          : (45.5444,  3.2488),
    "Thiers"           : (45.8553,  3.5433),
    "Ambert"           : (45.5492,  3.7425),
    "Brioude"          : (45.2941,  3.3868),
}

# Rayon de recherche autour du centre-ville (en mètres)
RADIUS = 5000

# ─────────────────────────────────────────────

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "CrowseekProspector/1.0"}


def query_overpass(key, value, lat, lng, radius):
    """Lance une requête Overpass pour un type d'établissement."""
    query = f"""
    [out:json][timeout:30];
    (
      node["{key}"="{value}"](around:{radius},{lat},{lng});
      way["{key}"="{value}"](around:{radius},{lat},{lng});
    );
    out body;
    """
    try:
        r = requests.post(
            OVERPASS_URL,
            data={"data": query},
            headers=HEADERS,
            timeout=35
        )
        if r.status_code == 200:
            return r.json().get("elements", [])
        else:
            print(f"\n  [!] Overpass erreur HTTP {r.status_code}")
            return []
    except requests.exceptions.Timeout:
        print(f"\n  [!] Timeout Overpass — réessaie dans quelques secondes")
        return []
    except Exception as e:
        print(f"\n  [!] Erreur Overpass : {e}")
        return []


def clean_phone(phone):
    """Normalise un numéro de téléphone au format français."""
    if not phone:
        return ""
    phone = phone.strip().replace(" ", "").replace("-", "").replace(".", "").replace("/", "")
    if phone.startswith("0033"):
        phone = "0" + phone[4:]
    elif phone.startswith("+33"):
        phone = "0" + phone[3:]
    # Formate en XX XX XX XX XX
    digits = phone.replace(" ", "")
    if len(digits) == 10:
        return " ".join([digits[i:i+2] for i in range(0, 10, 2)])
    return phone


def extract_info(element, category_label, city_name):
    """Extrait et filtre les infos d'un élément OSM."""
    tags = element.get("tags", {})

    # Filtre : garde uniquement ceux SANS site web
    if tags.get("website") or tags.get("contact:website") or tags.get("url"):
        return None

    name = tags.get("name", "").strip()
    if not name:
        return None  # Ignore les établissements sans nom

    phone = clean_phone(
        tags.get("phone") or
        tags.get("contact:phone") or
        tags.get("mobile") or
        tags.get("contact:mobile") or
        ""
    )

    email = (
        tags.get("email") or
        tags.get("contact:email") or
        ""
    ).strip()

    housenumber = tags.get("addr:housenumber", "").strip()
    street      = tags.get("addr:street", "").strip()
    address     = f"{housenumber} {street}".strip()

    ville       = tags.get("addr:city", city_name).strip()
    code_postal = tags.get("addr:postcode", "").strip()

    return {
        "Nom"             : name,
        "Adresse"         : address,
        "Ville"           : ville,
        "Code Postal"     : code_postal,
        "Téléphone"       : phone,
        "Email"           : email,
        "Catégorie"       : category_label,
        "Ville recherchée": city_name,
    }


def run():
    print("\n" + "═" * 56)
    print("  CROWSEEK PROSPECTOR — OpenStreetMap Edition")
    print("  Aucune clé API requise · Données OpenStreetMap")
    print("═" * 56 + "\n")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"prospects_crowseek_{timestamp}.csv"
    fieldnames = ["Nom", "Adresse", "Ville", "Code Postal",
                  "Téléphone", "Email", "Catégorie", "Ville recherchée"]

    seen_ids = set()
    total    = 0

    with open(filename, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        for city_name, (lat, lng) in CITIES.items():
            print(f"📍 Ville : {city_name}  ({lat}, {lng})")

            for key, value in CATEGORIES:
                label = value.replace("_", " ").capitalize()
                print(f"   🔍 {label:<20}", end="", flush=True)

                elements = query_overpass(key, value, lat, lng, RADIUS)
                time.sleep(1.2)  # Respecte la limite Overpass (1 req/s)

                count = 0
                for el in elements:
                    osm_id = el.get("id")
                    if osm_id in seen_ids:
                        continue
                    seen_ids.add(osm_id)

                    info = extract_info(el, label, city_name)
                    if info:
                        writer.writerow(info)
                        csvfile.flush()
                        count += 1
                        total += 1

                print(f"→ {count} prospect(s)")

            print()

    print("═" * 56)
    print(f"✅  {total} prospect(s) sans site web exporté(s)")
    print(f"📄  Fichier sauvegardé : {filename}")
    print("═" * 56)
    print()

    if total == 0:
        print("💡  Aucun résultat ? Vérifie ta connexion internet")
        print("    ou essaie d'augmenter le RADIUS dans la configuration.\n")
    else:
        print("💡  Conseil : l'email est rarement dans OSM.")
        print("    Pour le retrouver, cherche le nom de l'établissement")
        print("    sur Google et récupère l'email depuis leur site ou")
        print("    leur fiche Facebook.\n")


if __name__ == "__main__":
    run()
