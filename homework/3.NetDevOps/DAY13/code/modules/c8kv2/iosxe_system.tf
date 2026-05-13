resource "iosxe_system" "system" {
  provider       = iosxe.c8kv2
  hostname       = "C8Kv2"
  ip_domain_name = "lab.local"
}
