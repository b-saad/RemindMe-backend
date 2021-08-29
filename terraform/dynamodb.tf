

resource "aws_dynamodb_table" "events-dynamodb-table" {
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
    attribute_name = "TimeToExist"
    enabled        = false
  }

  tags = {
    Name        = "RemindMeEvents"
    Environment = "production"
  }

}
