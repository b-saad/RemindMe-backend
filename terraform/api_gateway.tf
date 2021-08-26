resource "aws_api_gateway_rest_api" "remind_me_api_gateway" {
  name        = "RemindMeApiGateway"
  description = "Gateway for Remind Me API"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.remind_me_api_gateway.id
  parent_id   = aws_api_gateway_rest_api.remind_me_api_gateway.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.remind_me_api_gateway.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}


resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.remind_me_api_gateway.id
  resource_id = aws_api_gateway_method.proxy.resource_id
  http_method = aws_api_gateway_method.proxy.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.remind_api_lambda.invoke_arn
}

resource "aws_api_gateway_method" "proxy_root" {
  rest_api_id   = aws_api_gateway_rest_api.remind_me_api_gateway.id
  resource_id   = aws_api_gateway_rest_api.remind_me_api_gateway.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_root" {
  rest_api_id = aws_api_gateway_rest_api.remind_me_api_gateway.id
  resource_id = aws_api_gateway_method.proxy_root.resource_id
  http_method = aws_api_gateway_method.proxy_root.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.remind_api_lambda.invoke_arn
}

resource "aws_api_gateway_deployment" "remind_me_api_gateway_deployment" {
  rest_api_id = aws_api_gateway_rest_api.remind_me_api_gateway.id
  triggers = {
    # NOTE: The configuration below will satisfy ordering considerations,
    #       but not pick up all future REST API changes. More advanced patterns
    #       are possible, such as using the filesha1() function against the
    #       Terraform configuration file(s) or removing the .id references to
    #       calculate a hash against whole resources. Be aware that using whole
    #       resources will show a difference after the initial implementation.
    #       It will stabilize to only change when resources change afterwards.
    redeployment = sha1(jsonencode([
      aws_api_gateway_integration.lambda.id,
      aws_api_gateway_integration.lambda_root.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "remind_me_api_gateway_stage" {
  deployment_id = aws_api_gateway_deployment.remind_me_api_gateway_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.remind_me_api_gateway.id
  stage_name    = "RemindMeAPI"
}
