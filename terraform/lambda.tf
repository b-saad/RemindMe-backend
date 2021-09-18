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
  timeout          = 30

  environment {
    variables = {
      LOG_LEVEL                          = "INFO"
      EVENT_TABLE_NAME                   = aws_dynamodb_table.events_dynamodb_table.name
      SMS_QUEUE_NAME                     = "${aws_sqs_queue.sms_queue.name}"
      EMAIL_QUEUE_NAME                   = "${aws_sqs_queue.email_queue.name}"
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
  name = "${var.remind_me_api_function_name}_lambda_role_policy"
  role = aws_iam_role.remind_me_api_lambda_role.id

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
      },
      {
          "Effect": "Allow",
          "Action": [
              "sqs:SendMessage",
              "sqs:GetQueueUrl"
          ],
          "Resource": [
              "${aws_sqs_queue.sms_queue.arn}",
              "${aws_sqs_queue.email_queue.arn}"
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


################################
##### Event Poller Lambda ######
################################

resource "aws_lambda_function" "event_poller_lambda" {
  role             = aws_iam_role.event_poller_lambda_role.arn
  handler          = "event_poller.handler"
  runtime          = var.runtime
  filename         = var.event_poller_lambda_zip_file
  function_name    = var.event_poller_function_name
  source_code_hash = filebase64sha256(var.event_poller_lambda_zip_file)
  timeout          = 120

  environment {
    variables = {
      LOG_LEVEL                   = "INFO"
      SMS_QUEUE_NAME              = aws_sqs_queue.sms_queue.name
      EMAIL_QUEUE_NAME            = aws_sqs_queue.email_queue.name
      EVENT_TABLE_NAME            = aws_dynamodb_table.events_dynamodb_table.name
      EVENT_TABLE_SECONDARY_INDEX = var.event_table_secondary_index_name
      EVENT_WINDOW_START_DELAY    = "300"
      EVENT_WINDOW_LENGTH         = var.storage_time_delta_minimum_seconds
    }
  }
}

resource "aws_iam_role" "event_poller_lambda_role" {
  name        = "${var.event_poller_function_name}_lambda_role"
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

resource "aws_iam_role_policy" "event_poller_lambda_role_policy" {
  name = "${var.event_poller_function_name}_lambda_role_policy"
  role = aws_iam_role.event_poller_lambda_role.id

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
              "dynamodb:GetItem",
              "dynamodb:BatchGetItem",
              "dynamodb:Scan",
              "dynamodb:Query",
              "dynamodb:ConditionCheckItem"
         ],
         "Resource": [
            "${aws_dynamodb_table.events_dynamodb_table.arn}/index/${var.event_table_secondary_index_name}"
         ]
      },
      {
          "Effect": "Allow",
          "Action": [
              "sqs:SendMessage",
              "sqs:GetQueueUrl"
          ],
          "Resource": [
              "${aws_sqs_queue.sms_queue.arn}",
              "${aws_sqs_queue.email_queue.arn}"
          ]
      }
  ]
}
EOF
}

#####################################
##### SMS Event Handler Lambda ######
#####################################

resource "aws_lambda_layer_version" "twilio_lambda_layer" {
  filename         = var.twilio_lambda_layer_zip_file
  layer_name       = "twilio_lambda_layer"
  source_code_hash = filebase64sha256(var.twilio_lambda_layer_zip_file)

  compatible_runtimes = ["python3.8", "python3.9"]
}

resource "aws_lambda_function" "sms_event_handler_lambda" {
  role             = aws_iam_role.sms_event_handler_lambda_role.arn
  handler          = "sms_event_handler.handler"
  runtime          = var.runtime
  filename         = var.sms_event_handler_lambda_zip_file
  function_name    = var.sms_event_handler_lambda_function_name
  source_code_hash = filebase64sha256(var.sms_event_handler_lambda_zip_file)
  timeout          = 120
  layers           = [aws_lambda_layer_version.twilio_lambda_layer.arn]

  environment {
    variables = {
      LOG_LEVEL           = "DEBUG"
      SMS_QUEUE_NAME      = aws_sqs_queue.sms_queue.name
      TWILIO_ACCOUNT_SID  = var.twilio_account_sid
      TWILIO_AUTH_TOKEN   = var.twilio_auth_token
      TWILIO_PHONE_NUMBER = var.twilio_phone_number
    }
  }
}

resource "aws_iam_role" "sms_event_handler_lambda_role" {
  name        = "${var.sms_event_handler_lambda_function_name}_lambda_role"
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

resource "aws_iam_role_policy" "sms_event_handler_lambda_role_policy" {
  name = "${var.sms_event_handler_lambda_function_name}_lambda_role_policy"
  role = aws_iam_role.sms_event_handler_lambda_role.id

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
            "sqs:ChangeMessageVisibility",
            "sqs:DeleteMessage",
            "sqs:GetQueueAttributes",
            "sqs:ReceiveMessage"
          ],
          "Resource": [
              "${aws_sqs_queue.sms_queue.arn}"
          ]
      }
  ]
}
EOF
}

resource "aws_lambda_event_source_mapping" "sms_event_handler_lambda_event_source_mapping" {
  event_source_arn = aws_sqs_queue.sms_queue.arn
  enabled          = true
  function_name    = aws_lambda_function.sms_event_handler_lambda.arn
}
