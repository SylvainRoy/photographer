# Configure the Azure provider
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.65"
    }
  }

  required_version = ">= 0.14.9"
}

provider "azurerm" {
  features {}
}

variable "dockerhub_username" {
  description = "Dockerhub username"
  type        = string
  sensitive   = true
}

variable "dockerhub_password" {
  description = "Dockerhub password"
  type        = string
  sensitive   = true
}

resource "azurerm_resource_group" "photographer" {
  name     = "photographer-resources"
  location = "West Europe"
}

resource "azurerm_container_group" "photographer" {
  name                = "photographer-continst"
  location            = azurerm_resource_group.photographer.location
  resource_group_name = azurerm_resource_group.photographer.name
  ip_address_type     = "public"
  dns_name_label      = "photographer-sroy"
  os_type             = "Linux"

  image_registry_credential {
    username = var.dockerhub_username
    password = var.dockerhub_password
    server   = "hub.docker.com"
  }

  container {
    name   = "photographer"
    image  = "sroy/photographer:latest"
    cpu    = "0.5"
    memory = "1.5"

    ports {
      port     = 8000
      protocol = "TCP"
    }
  }

  tags = {
    environment = "photographer"
  }
}
