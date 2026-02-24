# botasset

## Environnement de création d'assets

- Configuration principale: `.devcontainer/asset-creator/devcontainer.json`
- Workflow de création de Codespace: `.github/workflows/create-codespace.yml`

## Générateur d'assets premium (Codespace)

### 1) Préparer les dépendances

Dans le Codespace:

```bash
pip3 install -r requirements.txt
```

### 2) Configurer le token API

```bash
cp .env.example .env
```

Puis remplacez la valeur de `REPLICATE_API_TOKEN` dans `.env`.

### 3) Générer des images

Script principal: `generate_asset.py`

Moteur par défaut: `fluxGen` (FLUX via Replicate). Vous pouvez basculer vers SDXL avec `--engine sdxl`.

Exemples:

```bash
python3 generate_asset.py --prompt "un chevalier fantasy en armure dorée, style cartoon, fond transparent" --output chevalier
python3 generate_asset.py --engine fluxGen --prompt "icône premium d'épée magique, fond transparent" --num 2 --output epee
python3 generate_asset.py --prompt "icône de potion de mana, style pixel art 16-bit" --num 4 --output potion
python3 generate_asset.py --prompt "décors de forêt enchantée, vue de dessus pour jeu mobile" --width 1536 --height 1536 --mobile 1024 1024 --output foret
```

Les PNG sont enregistrés dans `assets/` (ou dans le dossier défini avec `--output-dir`).

## Déclenchement du Codespace

Ajoutez un commentaire d'issue contenant:

`/create-asset-space`

Le workflow GitHub Actions crée alors un Codespace sur `main` avec le devcontainer `asset-creator`.

## Prébuild Codespaces (optionnel)

1. Ouvrir le dépôt GitHub > **Settings** > **Codespaces** > **Set up prebuild**.
2. Sélectionner la branche `main`.
3. Sélectionner le fichier `.devcontainer/asset-creator/devcontainer.json`.
4. Activer les prebuilds pour accélérer le démarrage après chaque push.