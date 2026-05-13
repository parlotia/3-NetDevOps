resource "iosxe_bgp" "device_bgp" {
  provider             = iosxe.c8kv1
  asn                  = var.bgp_asn
  log_neighbor_changes = true
}

resource "iosxe_bgp_neighbor" "device_bgp_neighbor" {
  provider             = iosxe.c8kv1
  asn                  = iosxe_bgp.device_bgp.asn
  ip                   = var.bgp_neighbor_ip
  remote_as            = var.bgp_neighbor_remote_as
  log_neighbor_changes = true
  shutdown             = false
}

resource "iosxe_bgp_address_family_ipv4" "device_bgp_ipv4_unicast" {
  provider                   = iosxe.c8kv1
  asn                        = iosxe_bgp.device_bgp.asn
  af_name                    = "unicast"
  ipv4_unicast_networks_mask = var.bgp_networks
}

resource "iosxe_bgp_ipv4_unicast_neighbor" "device_bgp_ipv4_unicast_neighbor" {
  provider = iosxe.c8kv1
  asn      = iosxe_bgp.device_bgp.asn
  ip       = iosxe_bgp_neighbor.device_bgp_neighbor.ip
  activate = true

  depends_on = [
    iosxe_bgp_address_family_ipv4.device_bgp_ipv4_unicast
  ]
}
