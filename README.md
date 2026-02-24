# botasset

## Environnement de création d'assets

- Configuration principale: `.devcontainer/asset-creator/devcontainer.json`
- Workflow de création de Codespace: `.github/workflows/create-codespace.yml`

## Déclenchement du Codespace

Ajoutez un commentaire d'issue contenant:

`/create-asset-space`

Le workflow GitHub Actions crée alors un Codespace sur `main` avec le devcontainer `asset-creator`.

## Prébuild Codespaces (optionnel)

1. Ouvrir le dépôt GitHub > **Settings** > **Codespaces** > **Set up prebuild**.
2. Sélectionner la branche `main`.
3. Sélectionner le fichier `.devcontainer/asset-creator/devcontainer.json`.
4. Activer les prebuilds pour accélérer le démarrage après chaque push.