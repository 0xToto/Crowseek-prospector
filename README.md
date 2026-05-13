# Crowseek Prospector — OpenStreetMap Edition

Trouve automatiquement les établissements sans site web dans ta zone
et les exporte en CSV prêt à l'emploi.
Aucune clé API, aucun compte requis.

---

## Installation

```bash
pip install requests
```

---

## Utilisation

```bash
python prospector_osm.py
```

Le script génère un fichier `prospects_crowseek_YYYYMMDD_HHMMSS.csv`
que tu peux ouvrir directement dans Excel ou Google Sheets.

---

## Configuration (section en haut du fichier)

### Ajouter des villes

```python
CITIES = {
    "Clermont-Ferrand" : (45.7772, 3.0870),
    "Lyon"             : (45.7640, 4.8357),
    # Trouve les coordonnées sur https://www.latlong.net
}
```

### Ajouter des catégories

```python
CATEGORIES = [
    ("amenity", "restaurant"),
    ("shop",    "hairdresser"),
    # Liste complète : https://wiki.openstreetmap.org/wiki/Map_features
]
```

### Ajuster le rayon

```python
RADIUS = 5000  # mètres — augmente pour couvrir plus de zone
```

---

## Colonnes du CSV

| Colonne          | Contenu                                    |
|------------------|--------------------------------------------|
| Nom              | Nom de l'établissement                     |
| Adresse          | Rue et numéro                              |
| Ville            | Ville                                      |
| Code Postal      | Code postal                                |
| Téléphone        | Numéro (si renseigné dans OSM)             |
| Email            | Email (si renseigné dans OSM)              |
| Catégorie        | Type d'établissement                       |
| Ville recherchée | Ville ciblée lors de la recherche          |

---

## Limites à connaître

- OSM filtre ceux sans champ `website` dans sa base — certains
  établissements ont quand même un site non renseigné dans OSM.
- L'email est rarement présent dans OSM : complète-le manuellement
  en cherchant l'établissement sur Google ou Facebook.
- Les données OSM sont contributives : couverture variable selon les villes.

