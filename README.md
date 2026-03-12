# Projet Cloud Computing - Deploiement Automatise avec Terraform (Azure)

Deploiement automatise d'une application Flask sur **Microsoft Azure** avec Terraform : VM Linux, base de donnees PostgreSQL (Flexible Server), stockage Azure Blob Storage.

## Architecture

```
┌─────────────┐       ┌──────────────────┐       ┌───────────────────┐
│   Client     │──────▶│  VM Linux (Flask) │──────▶│  Azure Blob       │
│  (curl/web)  │       │  Port 5000        │       │  Storage           │
└─────────────┘       └──────┬───────────┘       │  (images/logs/     │
                              │                    │   static)          │
                              ▼                    └───────────────────┘
                       ┌──────────────────┐
                       │ PostgreSQL        │
                       │ Flexible Server   │
                       └──────────────────┘
```

**Composants deployes :**
- **VM Linux** : Ubuntu 22.04 (Standard_B1s) avec l'application Flask
- **PostgreSQL Flexible Server** : Base de donnees managee (v15)
- **Azure Blob Storage** : Containers `images`, `logs`, `static`
- **VNet** : Reseau virtuel avec sous-reseaux, NSG
- **Private DNS Zone** : Connexion privee VM <-> PostgreSQL

## Prerequisites

1. **Terraform** >= 1.0 installe
2. **Compte Azure** avec un abonnement actif (credits etudiants OK)
3. **Azure CLI** installe et connecte
4. **Cle SSH** generee localement

### Installer Terraform

**Windows (chocolatey) :**
```bash
choco install terraform
```

**Linux / macOS :**
```bash
sudo apt-get install -y terraform    # Debian/Ubuntu
brew install terraform                # macOS
```

Verifier :
```bash
terraform -version
```

### Installer Azure CLI et se connecter

**Windows :**
```bash
winget install -e --id Microsoft.AzureCLI
```

**Linux :**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

**Se connecter :**
```bash
az login
```

Recuperer votre Subscription ID :
```bash
az account show --query id -o tsv
```

### Generer une cle SSH (si necessaire)

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
```

## Installation rapide

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd projet-cloud-computing
```

### 2. Configurer les variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Editer `terraform.tfvars` :

```hcl
# Votre Subscription ID Azure (az account show --query id -o tsv)
azure_subscription_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
location              = "France Central"

# VM
admin_username       = "azureuser"
ssh_public_key_path  = "~/.ssh/id_rsa.pub"
ssh_private_key_path = "~/.ssh/id_rsa"

# Base de donnees
db_password = "MonMotDePasse_Fort!123"

# Stockage (globalement unique, minuscules, 3-24 caracteres, lettres+chiffres)
storage_account_name = "cloudprojetstore12345"
```

> **Important** : Le `storage_account_name` doit etre **globalement unique** sur Azure. Ajoutez des chiffres aleatoires.

### 3. Deployer l'infrastructure

```bash
cd terraform

# Se connecter a Azure
az login

# Initialiser Terraform
terraform init

# Previsualiser les changements
terraform plan

# Deployer (confirmer avec 'yes')
terraform apply
```

Le deploiement prend environ **10-15 minutes** (PostgreSQL Flexible Server est le plus long).

### 4. Recuperer les informations

Apres le deploiement, Terraform affiche :

```
app_url              = "http://<IP>:5000"
vm_public_ip         = "<IP>"
postgres_fqdn        = "<serveur>.postgres.database.azure.com"
storage_account_name = "cloudprojetstore12345"
ssh_command          = "ssh -i ~/.ssh/id_rsa azureuser@<IP>"
```

## Utilisation de l'API

### Endpoints disponibles

| Methode | URL | Description |
|---------|-----|-------------|
| GET | `/` | Info + liste des endpoints |
| GET | `/health` | Health check |
| GET | `/api/files` | Lister tous les fichiers |
| POST | `/api/files` | Uploader un fichier |
| GET | `/api/files/<id>` | Info d'un fichier |
| GET | `/api/files/<id>/download` | Telecharger un fichier |
| PUT | `/api/files/<id>` | Remplacer un fichier |
| DELETE | `/api/files/<id>` | Supprimer un fichier |
| GET | `/api/storage/containers` | Lister les containers Blob |
| GET | `/api/storage/list?container=images` | Lister les blobs d'un container |

### Exemples avec curl

```bash
# Health check
curl http://<IP>:5000/health

# Uploader une image
curl -X POST http://<IP>:5000/api/files \
  -F "file=@mon-image.png" \
  -F "category=images"

# Lister les fichiers
curl http://<IP>:5000/api/files

# Lister par categorie
curl http://<IP>:5000/api/files?category=images

# Telecharger un fichier (id=1)
curl http://<IP>:5000/api/files/1/download -o fichier_telecharge.png

# Supprimer un fichier
curl -X DELETE http://<IP>:5000/api/files/1

# Lister les containers Azure Blob
curl http://<IP>:5000/api/storage/containers

# Lister les blobs dans le container 'logs'
curl "http://<IP>:5000/api/storage/list?container=logs"
```

### Script de test automatise

```bash
chmod +x scripts/test_api.sh
./scripts/test_api.sh <VM_PUBLIC_IP>
```

## Connexion SSH a la VM

```bash
ssh -i ~/.ssh/id_rsa azureuser@<IP>

# Voir les logs de l'application
sudo journalctl -u flaskapp -f

# Redemarrer l'application
sudo systemctl restart flaskapp

# Voir le statut
sudo systemctl status flaskapp
```

## Structure du projet

```
projet-cloud-computing/
├── terraform/
│   ├── provider.tf              # Configuration du provider Azure
│   ├── main.tf                  # Ressources (VM, Blob, PostgreSQL, VNet)
│   ├── variables.tf             # Variables d'entree
│   ├── outputs.tf               # Valeurs de sortie
│   ├── terraform.tfvars.example # Exemple de configuration
│   └── .gitignore
├── app/
│   ├── app.py                   # Application Flask principale
│   ├── models.py                # Modeles SQLAlchemy (FileRecord)
│   ├── storage_service.py       # Service Azure Blob Storage
│   ├── config.py                # Configuration (env vars)
│   ├── init_db.py               # Script d'initialisation BDD
│   ├── wsgi.py                  # Point d'entree Gunicorn
│   └── requirements.txt         # Dependances Python
├── scripts/
│   ├── install.sh               # Script de provisioning VM
│   └── test_api.sh              # Script de test des endpoints
├── .gitignore
└── README.md
```

## Commandes Terraform essentielles

| Commande | Description |
|----------|-------------|
| `terraform init` | Initialise le repertoire, telecharge les providers |
| `terraform plan` | Affiche les changements prevus sans les appliquer |
| `terraform apply` | Cree/modifie l'infrastructure (demande confirmation) |
| `terraform apply -auto-approve` | Applique sans demander confirmation |
| `terraform output` | Affiche les valeurs de sortie |
| `terraform show` | Affiche l'etat actuel de l'infrastructure |
| `terraform destroy` | **Supprime toute l'infrastructure** |
| `terraform fmt` | Formate les fichiers .tf |
| `terraform validate` | Valide la syntaxe des fichiers .tf |

## Detruire l'infrastructure

Pour supprimer toutes les ressources Azure creees :

```bash
cd terraform
terraform destroy
```

Confirmer avec `yes`. Toutes les ressources (VM, PostgreSQL, Storage, VNet, etc.) seront supprimees.

> **Attention** : `terraform destroy` supprime tout, y compris les donnees dans Blob Storage et PostgreSQL.

## Detail des etapes du projet

### Etape 1 - Environnement Terraform
- Le provider Azure (`azurerm`) est configure dans `provider.tf`
- Les variables sont definies dans `variables.tf` et les valeurs dans `terraform.tfvars`
- Authentification via `az login` (Azure CLI)

### Etape 2 - Deploiement de l'infrastructure
- **VM** : Linux Ubuntu 22.04 `Standard_B1s`, IP publique statique, NSG (SSH + HTTP + port 5000)
- **Stockage** : Azure Storage Account avec 3 containers Blob prives (`images`, `logs`, `static`)
- **Base de donnees** : PostgreSQL Flexible Server v15, `B_Standard_B1ms`, reseau prive via subnet delegue + DNS prive

### Etape 3 - Backend connecte au stockage
- Flask expose une API CRUD complete
- Upload/download/suppression de fichiers via Azure Blob Storage (`azure-storage-blob`)
- Metadonnees stockees dans PostgreSQL (nom, taille, categorie, date)

### Etape 4 - Automatisation
- Le provisioner Terraform `remote-exec` execute `install.sh` sur la VM
- Le script installe Python, cree un virtualenv, configure le `.env`, cree un service systemd
- L'application demarre automatiquement et redemarre en cas de crash

### Etape 5 - Tests
- Script `test_api.sh` pour valider automatiquement tous les endpoints
- Verification manuelle possible avec curl ou Postman
- `terraform destroy` pour nettoyer toutes les ressources

## Problemes courants

| Probleme | Solution |
|----------|----------|
| `terraform init` echoue | Verifier la connexion internet et la version de Terraform |
| `az login` ne fonctionne pas | Installer Azure CLI et verifier le navigateur |
| Subscription ID invalide | Executer `az account show --query id -o tsv` |
| Storage account name exists | Le nom doit etre globalement unique, changer `storage_account_name` |
| PostgreSQL timeout | Attendre quelques minutes, le provisioning peut etre long |
| Port 5000 inaccessible | Verifier le NSG et que le service `flaskapp` est actif |
| SSH connection refused | Attendre que la VM soit entierement provisionee |
