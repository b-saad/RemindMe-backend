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

variable "sms_event_handler_lambda_function_name" {
  default = "sms-event-handler"
}

variable "sms_event_handler_lambda_timeout" {
  default = 120
}
variable "sms_event_handler_lambda_zip_file" {
  default = "sms-event-handler-lambda.zip"
}

variable "twilio_lambda_layer_zip_file" {
  default = "twilio-layer.zip"
}

variable "twilio_account_sid" {
  type      = string
  sensitive = true
}

variable "twilio_auth_token" {
  type      = string
  sensitive = true
}

variable "twilio_phone_number" {
  type      = string
  sensitive = true
}

variable "storage_time_delta_minimum_seconds" {
  description = "The amount of time that an event must be in the future to be stored in persistent store"
  default     = "600" # 10 mins
}
