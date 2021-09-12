################################
##### RemindMe API Lambda ######
################################

resource "aws_lambda_function" "remind_api_lambda" {
  role             = aws_iam_role.remind_me_api_lambda_role.arn
  handler          = "remind_me_api.handler"
  runtime          = var.runtime
  filename         = var.remind_me_api_lambda_zip_file
  function_name    = var.remind_me_api_function_name
  source_code_hash = filebase64sha256(var.remind_me_api_lambda_zip_file)

  environment {
    variables = {
      LOG_LEVEL = "INFO"
      EVENT_TABLE_NAME = aws_dynamodb_table.events_dynamodb_table.name
      SMS_QUEUE_NAME = ""
      EMAIL_QUEUE_NAME = ""
      STORAGE_TIME_DELTA_MINIMUM_SECONDS = var.storage_time_delta_minimum_seconds
    }
  }
}

resource "aws_iam_role" "remind_me_api_lambda_role" {
  name        = "${var.remind_me_api_function_name}_lambda_role"
  path        = "/"
  description = "Allows Lambda Function to call AWS services on your behalf."

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "remind_me_api_lambda_role_policy" {
  name = "${var.remind_me_api_function_name}_lambda_role"
  role = "${aws_iam_role.remind_me_api_lambda_role.id}"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
      {
        "Action": [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource": "arn:aws:logs:*:*:*",
        "Effect": "Allow"
      },
      {
         "Effect": "Allow",
         "Action": [
            "dynamodb:PutItem"
         ],
         "Resource": [
            "${aws_dynamodb_table.events_dynamodb_table.arn}"
         ]
      }
  ]
}
EOF
}



resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.remind_api_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # The /*/* portion grants access from any method on any resource
  # within the API Gateway "REST API".
  source_arn = "${aws_api_gateway_rest_api.remind_me_api_gateway.execution_arn}/*/*"
}
