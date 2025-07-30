# 🎨 Artbot – Convertisseur d'images en ASCII

**Artbot** est un outil Python permettant de :
- Scraper les images d'une page web (comme Unsplash),
- Télécharger une image à un index donné,
- Appliquer un redimensionnement et un flou optionnel,
- Convertir l'image en ASCII art,
- Générer un fichier HTML,
- Ou servir le résultat via une API FastAPI.

---

## ⚙️ Option 1 — Exécution en local (via GitHub)

### 🔧 Installation

Assurez-vous d’avoir **Python 3.8+** installé.

```bash
git clone https://github.com/NoaYnov/ArtBot
cd ArtBot
pip install -e .
```

### ▶️ Utilisation

```bash
python -m artbot --url <PAGE_URL> --index <N> [--blur <RAYON>] [--size <LARGEUR>]
```

Exemple :

```bash
python -m artbot --url https://unsplash.com/fr --index 3 --blur 2 --size 80
```

---

## 📦 Option 2 — Installation via PyPI (comme un module)

Le package est disponible sur PyPI sous le nom `artbot-Philippe-Noa`.

### 🔧 Installation

```bash
pip install artbot-Philippe-Noa
```

### ▶️ Utilisation via console :

```bash
artbot --url <PAGE_URL> --index <N> [--blur <RAYON>] [--size <LARGEUR>]
```

Si la commande `artbot` n’est pas reconnue :

```bash
py -m artbot --url <PAGE_URL> --index <N> [--blur <RAYON>] [--size <LARGEUR>]
```

---

## 🌐 Lancer l'API FastAPI

Depuis n’importe quelle version installée :

```bash
artbot --serve
```

ou

```bash
py -m artbot --serve
```

### Endpoint disponible

#### `POST /ascii`

Retourne le contenu HTML généré (`ascii_art.html`).

---

## 📂 Structure du projet

```
artbot/
├── __main__.py            # Point d'entrée CLI + API
├── api.py                 # Serveur FastAPI
├── fetch_images.py        # Scraping & téléchargement
├── pixel_to_ascii.py      # Conversion image → ASCII
img/
├── img.jpg                # Image brute
├── processed_img.jpg      # Image floutée/redimensionnée
result/
├── ascii_art.html         # Résultat HTML

setup.py
README.md
```

---

## 📄 Licence

Ce projet est sous licence MIT.
