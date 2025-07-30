IMAGE ?= devopness-mcp-server
TAG ?= latest

WORKDIR := mcp

.DEFAULT_GOAL := help
.PHONY: build-image shell update-version publish lint format help

##@ Docker

build-image: ## 🔧 Build the Docker image (optional: PYTHON_VERSION / ALPINE_VERSION)
	$(info 🐳 Building Docker image...)
	@docker build \
		-f Dockerfile \
		$(if $(PYTHON_VERSION),--build-arg PYTHON_VERSION=$(PYTHON_VERSION),) \
		$(if $(ALPINE_VERSION),--build-arg ALPINE_VERSION=$(ALPINE_VERSION),) \
		-t $(IMAGE):$(TAG) .

shell: build-image ## 🐚 Open a shell inside the MCP Server container
	$(info 🔧 Starting interactive shell in MCP Server container...)
	@docker run --rm -it \
		-v $(PWD):/$(WORKDIR) \
		--name devopness-mcp-server-shell \
		$(IMAGE):$(TAG) \
		/bin/bash

##@ MCP Server Publish
update-version: ## 📦 Update the MCP Server Version. Usage: make update-version TYPE=(major|minor|patch)
	@docker run --rm \
		-v $(PWD):/app \
		-w /app \
		--name devopness-mcp-server-update-version \
		--env TYPE=$(if $(TYPE),$(TYPE),'') \
		$(IMAGE):$(TAG) \
		/bin/bash -c '\
			set -e; \
			CURRENT_VERSION=$$(grep -E "^version" pyproject.toml | grep -oE "[0-9]+\.[0-9]+\.[0-9]+"); \
			IFS="." read -r MAJOR MINOR PATCH <<< "$$CURRENT_VERSION"; \
			\
			case "$$TYPE" in \
				major) MAJOR=$$((MAJOR + 1)); MINOR=0; PATCH=0 ;; \
				minor) MINOR=$$((MINOR + 1)); PATCH=0 ;; \
				patch) PATCH=$$((PATCH + 1)) ;; \
				\
				*)	echo "ERROR: TYPE must be major, minor or patch"; \
					echo "Usage: make update-version TYPE=(major|minor|patch)"; \
					exit 1 ;; \
			esac; \
			\
			NEW_VERSION="$$MAJOR.$$MINOR.$$PATCH"; \
			echo "Updating from $$CURRENT_VERSION to $$NEW_VERSION"; \
			sed -i "s/^version = \".*\"/version = \"$$NEW_VERSION\"/" pyproject.toml; \
			\
			# Sync new version in UV Lock File \
			uv lock; \
		'

publish: build-image ## 🚀 Publish the MCP Server to PyPI (requires PYPI_TOKEN)
	$(info 📦 Publishing MCP Server to PyPI...)
	@docker run --rm \
		-v $(PWD):/$(WORKDIR) \
		--env DEVOPNESS_MCP_SERVER_PYPI_TOKEN=$(PYPI_TOKEN) \
		--name devopness-mcp-server-publish \
		$(IMAGE):$(TAG) \
		/bin/bash -cex ' \
			uv build --no-cache; \
			uv publish --token "$$DEVOPNESS_MCP_SERVER_PYPI_TOKEN"; \
		'

##@ Lint & Format

lint: build-image ## 🔍 Run linting tools (ruff, mypy)
	$(info 🧹 Running linters...)
	@docker run --rm \
		-v $(PWD):/$(WORKDIR) \
		--name devopness-mcp-server-lint \
		$(IMAGE):$(TAG) \
		/bin/bash -cex ' \
			ruff check . && \
			ruff format . --check && \
			mypy . \
		'

format: build-image ## 🧼 Auto-format code with ruff
	$(info ✨ Formatting code...)
	@docker run --rm \
		-v $(PWD):/$(WORKDIR) \
		--name devopness-mcp-server-format \
		$(IMAGE):$(TAG) \
		/bin/bash -cex ' \
			ruff check --fix && \
			ruff format . \
		'

##@ Utilities

help: ## 📖 Show this help message
# `help` function obtained from https://gist.github.com/prwhite/8168133#gistcomment-4160123
	@echo "Devopness MCP Server"
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} \
	/^[a-zA-Z0-9_-]+:.*##/ { \
		printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 \
	}' $(MAKEFILE_LIST)
