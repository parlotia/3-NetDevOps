terraform {
  required_providers {
    iosxe = {
      source  = "CiscoDevNet/iosxe"
      version = "0.17.0"
    }
  }
}

provider "iosxe" {
  alias    = "c8kv2"
  username = var.DEVICE_LOGIN_USERNAME
  password = var.DEVICE_LOGIN_PASSWORD
  host     = "10.10.1.202"
  protocol = "restconf"
}
