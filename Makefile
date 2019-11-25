DOCKER_PROJECT=warehouse-api
DOCKER_USER=arkhn
GITHUB_SHA?=latest
DOCKER_TAG=$(GITHUB_SHA)

SERVICES=$(shell ls -d fhir-api)
BUILD_IMAGES=$(foreach service, $(SERVICES), build_docker_image_$(service))
PUBLISH_IMAGES=$(foreach service, $(SERVICES), publish_docker_image_$(service))


# == all ======================================================================
all: build

# == build ====================================================================
build: $(BUILD_IMAGES)

$(BUILD_IMAGES): build_docker_image_%: %/Dockerfile
	docker build -t $(DOCKER_USER)/$*:$(DOCKER_TAG) -f $*/Dockerfile $*

# == publish ====================================================================
publish: $(PUBLISH_IMAGES)

$(PUBLISH_IMAGES): publish_docker_image_%: %/Dockerfile
	docker push $(DOCKER_USER)/$*:$(DOCKER_TAG)
