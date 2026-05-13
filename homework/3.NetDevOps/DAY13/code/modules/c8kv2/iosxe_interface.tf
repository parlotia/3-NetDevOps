resource "iosxe_interface_ethernet" "interface_g2" {
  provider          = iosxe.c8kv2
  type              = "GigabitEthernet"
  name              = "2"
  description       = "Terraform Configure Interface G2"
  shutdown          = false
  ipv4_address      = "172.16.12.2"
  ipv4_address_mask = "255.255.255.0"
}

resource "iosxe_interface_loopback" "interface_loop0" {
  provider          = iosxe.c8kv2
  name              = 0
  description       = "Terraform Configure Interface Lo0"
  shutdown          = false
  ipv4_address      = "2.2.2.2"
  ipv4_address_mask = "255.255.255.0"
}

resource "iosxe_interface_loopback" "interface_loop1" {
  provider          = iosxe.c8kv2
  name              = 1
  description       = "Terraform Configure Interface Lo1"
  shutdown          = false
  ipv4_address      = "22.2.2.2"
  ipv4_address_mask = "255.255.255.0"
}
