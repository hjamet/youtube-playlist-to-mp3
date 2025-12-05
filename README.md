# YouTube Playlist MP3 Downloader 🎵📥

Télécharge des playlists YouTube entières et les convertit en fichiers MP3 de haute qualité.

## 🚀 Installation

### Installer Poetry

Ce projet utilise [Poetry](https://python-poetry.org/) pour gérer les dépendances.

**Linux/macOS :**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Windows (PowerShell) :**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

**Alternative :** Utilisez pip si Poetry n'est pas disponible :
```bash
pip install poetry
```

### Installer les dépendances

Une fois Poetry installé, installez les dépendances du projet :

```bash
poetry install
```

**Note :** Le script télécharge automatiquement `ffmpeg` si nécessaire. Aucune installation manuelle requise.

## 📖 Utilisation

### Exécuter le script

Avec Poetry, exécutez le script `toutDVD` :

```bash
poetry run python to_dvd.py "URL_DE_LA_PLAYLIST"
```

### Comment obtenir l'URL de la playlist

1. Allez sur la playlist YouTube dans votre navigateur
2. Copiez l'URL complète depuis la barre d'adresse
3. L'URL doit ressembler à : `https://www.youtube.com/playlist?list=PL1KFFrJTkUrO...`

### Options disponibles

```bash
# Téléchargement avec qualité par défaut (320 kbps)
poetry run python to_dvd.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"

# Téléchargement avec qualité personnalisée
poetry run python to_dvd.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID" -b 192

# Sans normalisation audio
poetry run python to_dvd.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID" --no-normalize
```

### Arguments

| Argument | Description | Défaut |
|----------|-------------|--------|
| `playlist_url` | URL de la playlist YouTube | Requis |
| `-b, --bitrate` | Bitrate audio en kbps (128, 192, 256, 320) | `320` |
| `--no-normalize` | Désactive la normalisation du volume audio | Activé par défaut |

## 📁 Fichiers générés

Les fichiers MP3 sont sauvegardés dans le dossier `musique/` à la racine du projet. Le dossier est créé automatiquement et nettoyé avant chaque nouveau téléchargement.

## ✨ Fonctionnalités

- **Téléchargement de playlist complète** : Télécharge toutes les vidéos d'une playlist en une commande
- **Qualité audio élevée** : Jusqu'à 320 kbps MP3
- **Normalisation audio** : Normalise automatiquement le volume de tous les fichiers
- **Validation** : Vérifie que tous les fichiers font moins de 79 minutes (pour compatibilité DVD)
- **Gestion d'erreurs** : Arrêt immédiat en cas d'erreur (fail-fast)

## 🐛 Dépannage

**Erreur "Poetry not found" :**
- Installez Poetry (voir section Installation)
- Vérifiez que Poetry est dans votre PATH

**Playlist URL ne fonctionne pas :**
- Vérifiez que la playlist est publique
- Copiez l'URL complète incluant le paramètre `list=`

**Erreurs de téléchargement :**
- Le script s'arrête immédiatement en cas d'erreur (fail-fast)
- Vérifiez votre connexion internet
- Vérifiez que la playlist est accessible

## 🔒 Considérations légales

- Téléchargez uniquement du contenu pour lequel vous avez la permission
- Respectez les Conditions d'utilisation de YouTube
- Utilisez à des fins personnelles, éducatives ou de fair use

---

**Bon téléchargement ! 🎶✨**
