data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "this" {
  statement {
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions   = ["es:*"]
    resources = ["arn:aws:es:${var.region}:${data.aws_caller_identity.current.account_id}:domain/${var.name}/*"]
  }
}

resource "aws_opensearch_domain" "rag" {
  domain_name    = var.name
  engine_version = "OpenSearch_2.7"

  node_to_node_encryption {
    enabled = var.opensearch_node_to_node_encryption
  }

  encrypt_at_rest {
    enabled = var.opensearch_encrypt_at_rest
  }

  domain_endpoint_options {
    enforce_https       = var.opensearch_domain_endpoint_options_enforce_https
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  cluster_config {
    instance_type            = var.opensearch_data_instance_type
    instance_count           = var.opensearch_data_instance_count
    dedicated_master_enabled = var.opensearch_cluster_config_dedicated_master_enabled
    warm_enabled             = var.opensearch_cluster_config_warm_enabled
  }

  ebs_options {
    ebs_enabled = var.opensearch_ebs_options_ebs_enabled
    volume_size = var.opensearch_ebs_options_volume_size
    volume_type = var.opensearch_ebs_options_volume_type
  }

  advanced_security_options {
    enabled                        = var.opensearch_advanced_security_options_enabled
    internal_user_database_enabled = var.opensearch_advanced_security_options_enabled_internal_user
    master_user_options {
      master_user_name     = var.name
      master_user_password = aws_secretsmanager_secret_version.secret.secret_string
    }
  }

  access_policies = data.aws_iam_policy_document.this.json

  depends_on = [aws_secretsmanager_secret.secret]
}

output "opensearch_url" {
  value = aws_opensearch_domain.rag.endpoint
}

output "opensearch_dashboard" {
  value = aws_opensearch_domain.rag.dashboard_endpoint
}