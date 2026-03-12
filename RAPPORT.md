# Rapport du projet – Déploiement cloud avec Terraform (Azure)

## Comment prendre les captures d’écran

### Sur Windows

1. **Outil Capture (Snipping Tool)**  
   - Touche Windows → taper « Capture » ou « Snipping Tool »  
   - Cliquer sur « Nouveau », sélectionner la zone à capturer  
   - Enregistrer (Ctrl+S) en PNG ou JPG  

2. **Raccourci rapide**  
   - **Win + Shift + S** : ouvre l’outil de capture d’écran  
   - Choisir « Rectangulaire » ou « Fenêtre »  
   - L’image est copiée dans le presse-papiers → coller (Ctrl+V) dans Word ou dans un fichier image  

3. **Capture de tout l’écran**  
   - **Imp. écran (Print Screen)** : capture tout l’écran  
   - Coller dans Word ou dans Paint puis enregistrer  

Conseil : faire les captures au moment où tu exécutes les commandes / où tu ouvres le portail Azure, pour que ce soit cohérent avec ton rapport.

---

## Comment visualiser ce qui a été déployé

### 1. Avec Terraform (dans le terminal)

Après `terraform apply`, tu peux revoir les infos à tout moment :

```bash
cd terraform
terraform output
```

Tu obtiens par exemple :
- **vm_public_ip** : l’IP de ta machine (ex: 20.251.203.214)
- **app_url** : l’URL de l’app (ex: http://20.251.203.214:5000)
- **storage_account_name** : le nom du compte de stockage
- **postgres_fqdn** : l’adresse du serveur PostgreSQL
- **resource_group** : le nom du groupe de ressources

À capturer : une capture de la sortie de `terraform output` pour montrer que le déploiement est bien terminé.

---

### 2. Dans le portail Azure

1. Va sur **https://portal.azure.com** et connecte-toi.  
2. Dans la barre de recherche en haut, tape le nom de ton **Resource Group** (ex: `flaskcloud-rg`).  
3. Clique sur le groupe de ressources.

Tu vois la liste de toutes les ressources créées, par exemple :
- **Machine virtuelle** (ex: flaskcloud-vm)
- **Compte de stockage** (ex: flaskcloudblob35g)
- **Serveur PostgreSQL** (ex: flaskcloud-pgserver)
- **Réseau virtuel** (ex: flaskcloud-vnet)
- **Adresse IP publique** (ex: flaskcloud-web-ip)
- **Groupes de sécurité réseau**, etc.

Tu peux cliquer sur chaque ressource pour voir les détails (config, état, région, etc.).

Captures utiles :
- La page du Resource Group avec la liste des ressources.
- La page de la VM (nom, état « En cours d’exécution », région).
- La page du compte de stockage → Conteneurs (images, logs, static).
- La page du serveur PostgreSQL (nom, base de données, état).

---

### 3. Tester l’application (navigateur + terminal)

**Dans le navigateur**  
Ouvre l’URL affichée dans `terraform output` pour `app_url`, par exemple :  
`http://20.251.203.214:5000`  
Tu dois voir la page d’accueil de l’API (JSON avec les endpoints).  
Capture : la page d’accueil dans le navigateur.

**Dans le terminal (curl)**

```bash
# Remplace <IP> par ton vm_public_ip (ex: 20.251.203.214)

# Page d'accueil
curl http://<IP>:5000/

# Health check
curl http://<IP>:5000/health

# Liste des fichiers (CRUD)
curl http://<IP>:5000/api/files
```

Captures utiles : la sortie de ces commandes dans le terminal pour montrer que l’API répond et que les données (fichiers) s’affichent.

---

### 4. Résumé : quoi capturer pour le rapport

| Quoi montrer | Où / Comment |
|--------------|--------------|
| Déploiement Terraform réussi | Sortie de `terraform output` dans le terminal |
| Ressources créées sur Azure | Portail Azure → ton Resource Group → liste des ressources |
| VM en cours d’exécution | Portail Azure → ta machine virtuelle |
| Stockage (conteneurs) | Portail Azure → Compte de stockage → Conteneurs |
| Base PostgreSQL | Portail Azure → Serveur PostgreSQL |
| API qui répond | Navigateur : `http://<IP>:5000` |
| Tests CRUD (liste, health) | Terminal : sortie de `curl` sur /health et /api/files |
| Suppression de l’infra | Sortie de `terraform destroy` (optionnel) |

---

## Rédaction type « étudiant » pour le rapport

Tu peux t’en inspirer pour rédiger ton rapport (à adapter avec tes vrais noms / captures).

**Introduction**  
« Dans ce TP, j’ai déployé une application web Flask sur Azure en utilisant Terraform. L’objectif était de créer une VM, un stockage (Blob) et une base PostgreSQL, puis de faire tourner l’application dessus et de la tester. »

**Étape 1 – Préparation**  
« J’ai installé Terraform et l’Azure CLI, puis je me suis connecté avec `az login`. J’ai configuré les variables dans un fichier `terraform.tfvars` (subscription ID, région, mot de passe de la base, nom du compte de stockage). Ma région autorisée par l’abonnement étudiant était Norway East. »

**Étape 2 – Déploiement**  
« J’ai lancé `terraform init` puis `terraform apply`. Le déploiement a créé un Resource Group, un réseau virtuel, une VM Ubuntu, un compte de stockage avec 3 conteneurs (images, logs, static) et un serveur PostgreSQL. J’ai vérifié dans le portail Azure que toutes les ressources apparaissent bien dans le groupe. »

**Étape 3 – Backend et stockage**  
« L’application Flask lit et écrit des fichiers dans Azure Blob Storage et enregistre les métadonnées dans PostgreSQL. J’ai testé avec `curl` : upload d’un fichier, liste des fichiers, téléchargement, suppression. Les fichiers apparaissent bien dans les conteneurs du portail Azure. »

**Étape 4 – Automatisation**  
« Un script `install.sh` est exécuté par Terraform sur la VM pour installer Python, les dépendances et lancer l’application en service. Comme ça, l’app redémarre toute seule si la VM redémarre. »

**Étape 5 – Tests et suppression**  
« J’ai vérifié l’accès à l’app via l’IP publique sur le port 5000, les appels à l’API et le contenu du stockage. À la fin, j’ai fait `terraform destroy` pour tout supprimer et ne pas consommer de crédits. »

**Problèmes rencontrés**  
« La région France Central n’était pas autorisée pour mon abonnement, j’ai dû utiliser Norway East. La taille de VM Standard_B1s n’était pas disponible partout, j’ai utilisé Standard_B2s_v2. J’ai aussi eu des soucis avec les fins de ligne (CRLF) dans le script sous Windows, corrigés avec `sed` sur la VM. »

Tu peux coller tes captures d’écran à côté de chaque paragraphe correspondant.
