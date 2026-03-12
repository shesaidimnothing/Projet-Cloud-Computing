# --- Azure ---
variable "azure_subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "France Central"
}

# --- Project ---
variable "project_name" {
  description = "Name prefix for all resources (lowercase, no spaces)"
  type        = string
  default     = "cloudprojet"
}

# --- VM ---
variable "vm_size" {
  description = "Azure VM size"
  type        = string
  default     = "Standard_B1s"
}

variable "admin_username" {
  description = "Admin username for the VM"
  type        = string
  default     = "azureuser"
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key file"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "ssh_private_key_path" {
  description = "Path to SSH private key file (for provisioners)"
  type        = string
  default     = "~/.ssh/id_rsa"
}

# --- PostgreSQL ---
variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "flaskdb"
}

variable "db_username" {
  description = "PostgreSQL admin username"
  type        = string
  default     = "flaskadmin"
}

variable "db_password" {
  description = "PostgreSQL admin password (min 8 chars, must include upper, lower, number)"
  type        = string
  sensitive   = true
}

# --- Storage ---
variable "storage_account_name" {
  description = "Azure Storage Account name (globally unique, lowercase, 3-24 chars, letters+numbers only)"
  type        = string
}
