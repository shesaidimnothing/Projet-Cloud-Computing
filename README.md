# Projet Cloud Computing - TP Terraform Azure

Projet de déploiement d'une app Flask sur Azure avec Terraform : une VM, une base PostgreSQL et un stockage (Blob) pour des fichiers.

## Captures d'écran et rapport

- **Comment prendre les captures** et **comment visualiser ce qui a été déployé** → voir **[RAPPORT.md](RAPPORT.md)**.
- Dans le rapport il y a aussi un **texte type "étudiant"** pour chaque étape et la liste des **captures à faire** (Terraform, portail Azure, navigateur, terminal).

---

## Ce qui est déployé

- Une **VM Linux** (Ubuntu) avec l'app Flask qui tourne sur le port 5000
- Un **stockage Azure Blob** avec 3 conteneurs : images, logs, static
- Une **base PostgreSQL** (Flexible Server) pour les métadonnées des fichiers
- Un **réseau** (VNet, IP publique, règles de sécurité)

L'app expose une API pour uploader / lister / télécharger / supprimer des fichiers ; les fichiers sont dans Blob et les infos en base.

---

## Prérequis

- Terraform installé
- Compte Azure (crédits étudiants ok)
- Azure CLI installé et connecté (`az login`)
- Une clé SSH (ex: `~/.ssh/id_rsa`)

---

## Installation et déploiement

### 1. Configurer les variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Ouvre `terraform.tfvars` et mets :
- ton **Subscription ID** Azure (`az account show --query id -o tsv`)
- la **région** (avec abo étudiant : une des autorisées, ex. Norway East, Sweden Central)
- le **chemin de ta clé SSH** (ex. `C:/Users/TonUser/.ssh/id_rsa.pub` et `.ssh/id_rsa`)
- un **mot de passe** pour PostgreSQL
- un **nom de compte de stockage** unique (minuscules, chiffres, 3–24 caractères)

### 2. Lancer le déploiement

```bash
terraform init
terraform plan    # pour voir ce qui va être créé
terraform apply   # confirmer avec yes
```

Ça prend environ 10–15 min (surtout PostgreSQL).

### 3. Récupérer l'IP et tester

```bash
terraform output
```

Tu obtiens `vm_public_ip` et `app_url`. Dans le navigateur ou avec curl :

```bash
curl http://<IP>:5000/
curl http://<IP>:5000/health
curl http://<IP>:5000/api/files
```

---

## Voir ce qui a été déployé

- **Terminal** : `terraform output` donne l'IP, l'URL de l'app, le nom du storage, etc.
- **Portail Azure** : portal.azure.com → chercher ton Resource Group (ex. `flaskcloud-rg`) → tu vois la VM, le stockage, PostgreSQL, le réseau.
- **App** : ouvrir `http://<IP>:5000` dans le navigateur pour voir l'API.

Détails et idées de captures pour le rapport → **[RAPPORT.md](RAPPORT.md)**.

---

## Structure du projet

```
terraform/     → fichiers .tf (provider, main, variables, outputs)
app/           → code Flask (app.py, models, config, storage_service, etc.)
scripts/       → install.sh (provisioning VM), test_api.sh (tests)
RAPPORT.md     → captures d'écran, visualisation, rédaction type étudiant
```

---

## Commandes utiles

- `terraform output` → afficher les sorties (IP, URL, etc.)
- `terraform destroy` → tout supprimer (à faire à la fin du TP pour ne pas consommer de crédits)

---

## Détruire l'infrastructure

```bash
cd terraform
terraform destroy
```

Confirmer avec `yes`. Tout est supprimé (VM, base, stockage, réseau).
