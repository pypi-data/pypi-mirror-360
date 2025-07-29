# Makefile for Escobar JupyterLab Extension

# Configuration
IMAGE_NAME = escobar-jupyterlab
CONTAINER_NAME = escobar-jupyterlab
HOST_PORT_JUPYTER = 8888

# Get host IP for SERVER_URL (works on Linux/macOS)
HOST_IP := $(shell ipconfig getifaddr en0 2>/dev/null || hostname -I | awk '{print $$1}')

.PHONY: build run stop logs clean 

# Build the Docker image with PyPI escobar
build:
	@echo "Building Docker image: $(IMAGE_NAME)"
	docker build --no-cache -t $(IMAGE_NAME) .

# Build Docker image with dev code.
build-dev:
	@echo "Building Docker image: $(IMAGE_NAME)"
	docker build -f Dockerfile.dev --no-cache -t $(IMAGE_NAME) .

# Run the Docker container
run:
	docker rm -f $(CONTAINER_NAME)
	docker run -d --name $(CONTAINER_NAME) \
		-p $(HOST_PORT_JUPYTER):8888 \
		$(IMAGE_NAME)
	@echo "Container started. Run 'make logs' to view the output."

stop:
	@echo "Stopping container: $(CONTAINER_NAME)"
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

logs:
	@echo "Viewing logs for container: $(CONTAINER_NAME)"
	docker logs -f $(CONTAINER_NAME)

clean: stop
	@echo "Removing Docker image: $(IMAGE_NAME)"
	docker rmi $(IMAGE_NAME) || true
	@echo "Removing docker-config directory"

