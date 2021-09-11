

resource "aws_dynamodb_table" "events_dynamodb_table" {
  name           = "RemindMeEvents"
  billing_mode   = "PROVISIONED"
  read_capacity  = 10
  write_capacity = 10
  hash_key       = "EventId"
  range_key      = "EventTimestamp"

  attribute {
    name = "EventId"
    type = "S"
  }

  attribute {
    name = "EventTimestamp"
    type = "N"
  }

  ttl {
    attribute_name = "TimeToLive"
    enabled        = true
  }

  tags = {
    Name        = "RemindMeEvents"
    Environment = "production"
  }

}
