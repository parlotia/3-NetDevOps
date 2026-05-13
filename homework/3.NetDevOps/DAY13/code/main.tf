module "c8kv1" {
  source                = "./modules/c8kv1"
  DEVICE_LOGIN_USERNAME = var.DEVICE_LOGIN_USERNAME
  DEVICE_LOGIN_PASSWORD = var.DEVICE_LOGIN_PASSWORD
}

module "c8kv2" {
  source                = "./modules/c8kv2"
  DEVICE_LOGIN_USERNAME = var.DEVICE_LOGIN_USERNAME
  DEVICE_LOGIN_PASSWORD = var.DEVICE_LOGIN_PASSWORD
}
