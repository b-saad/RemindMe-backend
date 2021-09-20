resource "aws_sqs_queue" "sms_queue" {
  name                       = "remind-me-sms-events"
  message_retention_seconds  = 600
  visibility_timeout_seconds = var.sms_event_handler_lambda_timeout
  tags = {
    Environment = "production"
    EventType   = "sms"
  }
}

resource "aws_sqs_queue" "email_queue" {
  name                       = "remind-me-email-events"
  message_retention_seconds  = 600
  visibility_timeout_seconds = 120

  tags = {
    Environment = "production"
    EventType   = "email"
  }
}
