# Projet Cloud - Terraform + Flask sur Azure

TP : déployer une app Flask avec Terraform (VM, PostgreSQL, Blob Storage).

**Rapport / captures** → [RAPPORT.md](RAPPORT.md)

## Prérequis

Terraform, Azure CLI (`az login`), clé SSH.

## Déployer

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# éditer terraform.tfvars (subscription ID, région, mot de passe BDD, nom du storage)
terraform init
terraform apply
```

Régions possibles avec abo efrei : Norway East, Sweden Central, etc. (voir erreur Azure si ta région est refusée).

Récupérer l’IP : `terraform output` → tester avec `curl http://<IP>:5000/`

## Tout supprimer

```bash
cd terraform
terraform destroy
```
