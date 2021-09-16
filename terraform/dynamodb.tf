

resource "aws_dynamodb_table" "events_dynamodb_table" {
  name           = "RemindMeEvents"
  billing_mode   = "PROVISIONED"
  read_capacity  = 3
  write_capacity = 5
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

  attribute {
    name = "EventWindowStart"
    type = "N"
  }

  ttl {
    attribute_name = "TimeToLive"
    enabled        = true
  }

  global_secondary_index {
    name            = var.event_table_secondary_index_name
    hash_key        = "EventWindowStart"
    range_key       = "EventTimestamp"
    write_capacity  = 5
    read_capacity   = 7
    projection_type = "ALL"
  }

  tags = {
    Name        = "RemindMeEvents"
    Environment = "production"
  }

}
