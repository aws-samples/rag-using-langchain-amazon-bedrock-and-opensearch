data "aws_iam_policy_document" "bedrock" {
  statement {
    sid       = 1
    actions   = ["bedrock:InvokeModel"]
    resources = ["arn:aws:bedrock:*::foundation-model/*"]
  }
  statement {
    sid       = 2
    actions   = ["sts:AssumeRole"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "bedrock" {
  name   = "bedrock"
  policy = data.aws_iam_policy_document.bedrock.json
}

resource "aws_iam_role" "bedrock" {
  name               = "bedrock"
  assume_role_policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Statement1",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
  POLICY
}

resource "aws_iam_role_policy_attachment" "eks_cluster_autoscaling" {
  policy_arn = aws_iam_policy.bedrock.arn
  role       = aws_iam_role.bedrock.name
}

output "bedrock_role" {
  value = aws_iam_role.bedrock.arn
}