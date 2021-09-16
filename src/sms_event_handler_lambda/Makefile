lambda_zip_name = sms-event-handler-lambda.zip

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

.PHONY: package
package:
	cd src; zip -r ../$(lambda_zip_name) ./*
	mv $(lambda_zip_name) ../../terraform/ 
