lambda_zip_name = sms-event-handler-lambda.zip
twilio_layer_zip_name = twilio-layer.zip
mkfile_path := THIS_DIR := $(dir $(abspath $(firstword $(MAKEFILE_LIST))))

.PHONY: all
all: test

.PHONY: build-docker-sms-event-handler-lambda
build-docker-sms-event-handler-lambda:
	docker build -t docker-sms-event-handler-lambda .

.PHONY: clean
clean:
	docker image rm -f docker-sms-event-handler-lambda

.PHONY: test
test: build-docker-sms-event-handler-lambda
	docker run -t --rm docker-sms-event-handler-lambda pytest

.PHONY: twilio-layer
twilio-layer:
	./twilio-layer/create_layer.sh
	cd twilio-layer; zip -r ../$(twilio_layer_zip_name) python
	mv $(twilio_layer_zip_name) ../../terraform/ 	

.PHONY: package 
package:
	cd src; zip -r ../$(lambda_zip_name) ./*
	mv $(lambda_zip_name) ../../terraform/ 


