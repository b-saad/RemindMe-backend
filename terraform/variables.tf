variable "event_poller_function_name" {
  default = "event-poller"
}

variable "event_poller_lambda_zip_file" {
  default = "event-poller-lambda.zip"
}

variable "event_table_secondary_index_name" {
  default = "EventTimestampIndex"
}

variable "remind_me_api_function_name" {
  default = "remind-me-api"
}

variable "remind_me_api_lambda_zip_file" {
  default = "remind-me-api-lambda.zip"
}

variable "runtime" {
  default = "python3.9"
}

variable "storage_time_delta_minimum_seconds" {
  description = "The amount of time that an event must be in the future to be stored in persistent store"
  default     = "600" # 10 mins
}
