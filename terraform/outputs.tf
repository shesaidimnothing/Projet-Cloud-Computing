output "vm_public_ip" {
  description = "Public IP address of the VM"
  value       = azurerm_public_ip.web.ip_address
}

output "app_url" {
  description = "URL to access the Flask application"
  value       = "http://${azurerm_public_ip.web.ip_address}:5000"
}

output "storage_account_name" {
  description = "Azure Storage Account name"
  value       = azurerm_storage_account.main.name
}

output "postgres_fqdn" {
  description = "PostgreSQL server FQDN"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "postgres_database" {
  description = "PostgreSQL database name"
  value       = azurerm_postgresql_flexible_server_database.main.name
}

output "ssh_command" {
  description = "SSH command to connect to the VM"
  value       = "ssh -i ${var.ssh_private_key_path} ${var.admin_username}@${azurerm_public_ip.web.ip_address}"
}

output "resource_group" {
  description = "Azure Resource Group name"
  value       = azurerm_resource_group.main.name
}
