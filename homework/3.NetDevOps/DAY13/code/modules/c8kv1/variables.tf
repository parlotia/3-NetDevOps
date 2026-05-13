variable "DEVICE_LOGIN_USERNAME" {
  description = "Cisco IOS XE device login username"
  type        = string
  sensitive   = true
}

variable "DEVICE_LOGIN_PASSWORD" {
  description = "Cisco IOS XE device login password"
  type        = string
  sensitive   = true
}

variable "bgp_asn" {
  type        = string
  description = "Local BGP AS number"
  default     = "65001"
}

variable "bgp_neighbor_ip" {
  type        = string
  description = "BGP neighbor IP address"
  default     = "172.16.12.2"
}

variable "bgp_neighbor_remote_as" {
  type        = string
  description = "Remote BGP AS number"
  default     = "65002"
}

variable "bgp_networks" {
  description = "Loopback networks advertised by BGP"
  type = list(object({
    network = string
    mask    = string
  }))
  default = [
    {
      network = "1.1.1.0"
      mask    = "255.255.255.0"
    },
    {
      network = "11.1.1.0"
      mask    = "255.255.255.0"
    }
  ]
}
