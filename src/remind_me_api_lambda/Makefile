lambda_zip_name = remind-me-api-lambda.zip

.PHONY: all
all: test

.PHONY: build-docker-remind-me-api-lambda
build-docker-remind-me-api-lambda:
	docker build -t docker-remind-me-api-lambda .

.PHONY: clean
clean:
	docker image rm -f docker-remind-me-api-lambda

.PHONY: test
test: build-docker-remind-me-api-lambda
	docker run -t --rm docker-remind-me-api-lambda pytest

.PHONY: package
package:
	cd src; zip -r ../$(lambda_zip_name) ./*
	mv $(lambda_zip_name) ../../terraform/ 
