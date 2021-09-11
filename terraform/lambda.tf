################################
##### RemindMe API Lambda ######
################################

resource "aws_lambda_function" "remind_api_lambda" {
  role             = aws_iam_role.remind_me_api_lambda_role.arn
  handler          = "lambda.handler"
  runtime          = var.runtime
  filename         = var.remind_me_api_lambda_zip_file
  function_name    = var.remind_me_api_function_name
  source_code_hash = filebase64sha256(var.remind_me_api_lambda_zip_file)
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
         "Effect": "Allow",
         "Action": [
            "logs:*"
         ],
         "Resource": [
            "*"
         ]
      }
  ]
}
EOF
}

# ,
#       {
#          "Effect": "Allow",
#          "Action": [
#             "dynamodb:*"
#          ],
#          "Resource": [
#             "${aws_dynamo_db.events-dynamodb-table.arn}"
#          ]
#       }

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.remind_api_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # The /*/* portion grants access from any method on any resource
  # within the API Gateway "REST API".
  source_arn = "${aws_api_gateway_rest_api.remind_me_api_gateway.execution_arn}/*/*"
}
