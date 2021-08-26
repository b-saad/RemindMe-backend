output "remind_me_api_gateway_url" {
  value = aws_api_gateway_stage.remind_me_api_gateway_stage.invoke_url
}
