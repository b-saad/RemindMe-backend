lambda_zip_name = event-poller-lambda.zip

.PHONY: all
all: test

.PHONY: build-docker-event-poller-lambda
build-docker-event-poller-lambda:
	docker build -t docker-event-poller-lambda .

.PHONY: clean
clean:
	docker image rm -f docker-event-pollerlambda

.PHONY: test
test: build-docker-event-poller-lambda
	docker run -t --rm docker-event-poller-lambda pytest

.PHONY: package
package:
	cd src; zip -r ../$(lambda_zip_name) ./*
	mv $(lambda_zip_name) ../../terraform/ 
