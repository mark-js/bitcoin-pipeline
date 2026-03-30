variable "project" {
  type    = string
  sensitive = true
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "multi_region" {
  type    = string
  default = "US"
}

variable "location_code" {
  type    = string
  default = "us"
}