resource "iosxe_system" "system" {
  provider       = iosxe.c8kv1
  hostname       = "C8Kv1"
  ip_domain_name = "lab.local"
}
