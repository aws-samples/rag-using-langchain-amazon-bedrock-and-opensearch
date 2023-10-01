# General variables
variable "region" {
  default     = "us-east-1"
  description = "The region you want to deploy the solution"
}

variable "name" {
  default     = "rag"
  description = "the name for resource"
}

# Opensearch variables
variable "opensearch_data_instance_type" {
  default     = "r6g.large.search"
  description = "OpenSearch data instance type"
}

variable "opensearch_data_instance_count" {
  default     = 2
  description = "OpenSearch data instance count"
}

variable "opensearch_node_to_node_encryption" {
  default     = true
  description = "Opensearch node to node encryption"
}

variable "opensearch_encrypt_at_rest" {
  default     = true
  description = "Opensearch encryption at rest"
}

variable "opensearch_domain_endpoint_options_enforce_https" {
  default     = true
  description = "OpenSearch domain enforce https"
}

variable "opensearch_cluster_config_dedicated_master_enabled" {
  default = false
}

variable "opensearch_cluster_config_warm_enabled" {
  default = false
}

variable "opensearch_ebs_options_ebs_enabled" {
  default = true
}

variable "opensearch_ebs_options_volume_size" {
  default = 100
}

variable "opensearch_ebs_options_volume_type" {
  default = "gp3"
}

variable "opensearch_advanced_security_options_enabled" {
  default = true
}

variable "opensearch_advanced_security_options_enabled_internal_user" {
  default = true
}