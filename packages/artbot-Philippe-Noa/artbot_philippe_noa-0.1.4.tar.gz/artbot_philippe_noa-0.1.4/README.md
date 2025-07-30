# 🎨 Artbot – Convertisseur d'images en ASCII

**Artbot** est un outil Python permettant de :
- Scraper les images d'une page web (comme Unsplash),
- Télécharger une image à un index donné,
- Appliquer un redimensionnement et un flou optionnel,
- Convertir l'image en ASCII art,
- Générer un fichier HTML,
- Ou servir le résultat via une API FastAPI.

---

## 🚀 Installation

Assurez-vous d’avoir **Python 3.8+** installé.

### 1. Cloner le dépôt

```bash
git clone <url-du-repo>
cd ArtBot
```

### 2. Installer le projet

```bash
pip install -e .
```

Cela installe toutes les dépendances et rend la commande CLI `artbot` disponible.

---

## 💻 Utilisation en ligne de commande

```bash
artbot --url <PAGE_URL> --index <N> [--blur <RAYON>] [--size <LARGEUR>]
```

### Paramètres :
- `--url` : URL d'une page contenant des images (ex: [unsplash.com/fr](https://unsplash.com/fr))
- `--index` : Position de l'image à télécharger (1 = première image)
- `--blur` : (optionnel) Rayon de flou à appliquer (par défaut : 0)
- `--size` : (optionnel) Largeur de l'ASCII art en caractères (par défaut : 100)

### Exemple :

```bash
artbot --url https://unsplash.com/fr --index 3 --blur 2 --size 80
```

➡ Cela télécharge la 3e image, applique un flou, et génère un fichier `ascii_art.html`.

---

## 🌐 Utilisation en API (FastAPI)

### Lancer le serveur API :

```bash
artbot --serve
```

### Endpoints disponibles :

#### `POST /ascii`

Retourne le contenu HTML du fichier `ascii_art.html` (généré préalablement par la CLI).

- **Méthode :** `POST`
- **Réponse :** HTML affichant l’art ASCII

---

## 📂 Structure du projet

```
artbot/
├── __main__.py            # Point d'entrée CLI + API
├── api.py                 # Serveur FastAPI
├── fetch_images.py        # Scraping & téléchargement
├── pixel_to_ascii.py      # Conversion image → ASCII
img/
├── img.jpg                # Image téléchargée
├── processed_img.jpg      # Image redimensionnée/floutée
result/
├── ascii_art.html             # Résultat ASCII au format HTML

setup.py
README.md
```

---

## 🧠 Détails techniques

- `fetch_images.py` :
  - Scrape les balises `<img>` d'une page HTML.
  - Télécharge l'image selon l’index spécifié.

- `pixel_to_ascii.py` :
  - Convertit une image PIL en ASCII avec une largeur définie.
  - Gère la conversion vers un fichier HTML stylisé.

- `api.py` :
  - Expose `/ascii` via FastAPI pour afficher le HTML.

- `__main__.py` :
  - Sert d’interface CLI principale (`--url`, `--index`, `--blur`, `--size`)
  - Ou lance l’API (`--serve`)

---

## 📄 Licence

Ce projet est sous licence MIT.
