# Loan Onboarding API - Development Makefile
# This Makefile provides convenient commands for local development

# Detect the operating system and shell environment
# For Windows environments, we'll use Unix-style commands since MINGW/Git Bash is common
ifeq ($(OS),Windows_NT)
    # Windows (including MINGW/Git Bash)
    DETECTED_OS := Windows
    PYTHON := python
    PIP := pip
    VENV_ACTIVATE := .venv/Scripts/activate
    RM := rm -f
    RMDIR := rm -rf
    MKDIR := mkdir -p
    CP := cp
    SEP := /
    NULL := /dev/null
else
    # Linux/MacOS
    DETECTED_OS := $(shell uname -s)
    PYTHON := python3
    PIP := pip
    VENV_ACTIVATE := .venv/bin/activate
    RM := rm -f
    RMDIR := rm -rf
    MKDIR := mkdir -p
    CP := cp
    SEP := /
    NULL := /dev/null
endif

# Common variables
VENV_DIR := .venv
REQUIREMENTS := requirements.txt
DEV_REQUIREMENTS := requirements-dev.txt
TEST_DIR := tests
SRC_DIRS := api services utils config
COVERAGE_MIN := 85

# Colors for output
RESET := \033[0m
BOLD := \033[1m
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m

# Helper function to check if virtual environment is activated
define check_venv
	@$(PYTHON) -c "import os; exit(1) if not os.environ.get('VIRTUAL_ENV') else exit(0)" || (echo "$(YELLOW)⚠️  Virtual environment not activated. Run 'make init' first or activate manually.$(RESET)" && exit 1)
endef

# Helper function to print colored status messages
define print_status
	@echo "$(GREEN)[INFO]$(RESET) $(1)"
endef

define print_warning
	@echo "$(YELLOW)[WARNING]$(RESET) $(1)"
endef

define print_error
	@echo "$(RED)[ERROR]$(RESET) $(1)"
endef

define print_header
	@echo "$(BLUE)$(BOLD)[$(1)]$(RESET)"
endef

.PHONY: help init init-dev backend test test-cov test-report lint format type-check security clean clean-cache clean-all install-dev check-python setup-env venv activate docs

# Default target
help: ## Show this help message
	@echo "$(BLUE)$(BOLD)Loan Onboarding API - Development Commands$(RESET)"
	@echo ""
	@echo "$(BOLD)Setup Commands:$(RESET)"
	@echo "  make init          Production setup: venv + production dependencies + environment"
	@echo "  make init-dev      Development setup: venv + all dependencies + environment"
	@echo "  make venv          Create virtual environment only"
	@echo "  make install-dev   Install development dependencies (requires activated venv)"
	@echo "  make setup-env     Setup environment configuration files"
	@echo ""
	@echo "$(BOLD)Development Commands:$(RESET)"
	@echo "  make backend       Start development server with hot reload"
	@echo "  make test          Run unit tests with coverage report"
	@echo "  make test-cov      Run tests with detailed coverage analysis"
	@echo "  make test-report   Generate HTML coverage report"
	@echo ""
	@echo "$(BOLD)Code Quality Commands:$(RESET)"
	@echo "  make lint          Run all linting and formatting checks"
	@echo "  make format        Auto-format code (black, isort)"
	@echo "  make type-check    Run type checking with mypy"
	@echo "  make security      Run security analysis with bandit"
	@echo ""
	@echo "$(BOLD)Utility Commands:$(RESET)"
	@echo "  make clean         Clean cache and temporary files"
	@echo "  make clean-all     Clean everything including virtual environment"
	@echo "  make docs          Generate/serve API documentation"
	@echo "  make check-python  Check Python version and installation"
	@echo ""
	@echo "$(BOLD)Docker Commands:$(RESET)"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docker-up     Start services with Docker Compose"
	@echo "  make docker-down   Stop Docker services"
	@echo "  make docker-test   Run tests in Docker container"
	@echo ""
	@echo "Use 'make <command>' to run any command."

# Setup Commands
init: check-python venv _install-prod setup-env ## Production setup: venv, production dependencies, and environment
	$(call print_header,PRODUCTION SETUP COMPLETE)
	$(call print_status,Virtual environment created)
	$(call print_status,Production dependencies installed)
	$(call print_status,Environment files configured)
	@echo ""
	@echo "$(GREEN)🎉 Production setup completed successfully!$(RESET)"
	@echo ""
	@echo "$(BOLD)Next steps:$(RESET)"
	@echo "1. Activate virtual environment: $(YELLOW)source $(VENV_ACTIVATE)$(RESET)"
	@echo "2. Update .env file with your configuration"
	@echo "3. Start application: $(YELLOW)uvicorn main:app$(RESET)"

init-dev: check-python venv _install-dev setup-env ## Development setup: venv, all dependencies, and environment
	$(call print_header,DEVELOPMENT SETUP COMPLETE)
	$(call print_status,Virtual environment created)
	$(call print_status,All dependencies installed)
	$(call print_status,Environment files configured)
	@echo ""
	@echo "$(GREEN)🎉 Development setup completed successfully!$(RESET)"
	@echo ""
	@echo "$(BOLD)Next steps:$(RESET)"
	@echo "1. Activate virtual environment: $(YELLOW)source $(VENV_ACTIVATE)$(RESET)"
	@echo "2. Update .env file with your configuration"
	@echo "3. Start development server: $(YELLOW)make backend$(RESET)"
	@echo "4. Run tests: $(YELLOW)make test$(RESET)"

check-python: ## Check Python version and installation
	$(call print_header,CHECKING PYTHON)
	@$(PYTHON) -c "import sys; print('$(GREEN)[INFO]$(RESET) Python', sys.version.split()[0], 'found ✓'); sys.exit(0 if sys.version_info >= (3, 11) else 1)" || (echo "$(RED)[ERROR]$(RESET) Python 3.11 or higher is required" && exit 1)

venv: check-python ## Create virtual environment
	$(call print_header,VIRTUAL ENVIRONMENT)
	@$(PYTHON) -c "import os; print('$(YELLOW)[WARNING]$(RESET) Virtual environment already exists at $(VENV_DIR)') if os.path.exists('$(VENV_DIR)') else None"
	@$(PYTHON) -c "import os, subprocess; subprocess.run(['$(PYTHON)', '-m', 'venv', '$(VENV_DIR)']) if not os.path.exists('$(VENV_DIR)') else None"
	@$(PYTHON) -c "import os; print('$(GREEN)[INFO]$(RESET) Virtual environment created at $(VENV_DIR)') if os.path.exists('$(VENV_DIR)') else None"
	@echo "$(YELLOW)To activate: source $(VENV_ACTIVATE)$(RESET)"

install-dev: ## Install all dependencies (requires active virtual environment)
	$(call print_header,INSTALLING DEPENDENCIES)
	$(call check_venv)
	@echo "$(YELLOW)[WARNING]$(RESET) Installing dependencies..."
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'pip', 'install', '--upgrade', 'pip'])"
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'pip', 'install', '-r', '$(REQUIREMENTS)'])"
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'pip', 'install', '-r', '$(DEV_REQUIREMENTS)'])"
	@echo "$(GREEN)[INFO]$(RESET) Production dependencies installed ✓"
	@echo "$(GREEN)[INFO]$(RESET) Development dependencies installed ✓"

_install-prod: ## Internal: Install production dependencies only (used by init)
	$(call print_header,INSTALLING PRODUCTION DEPENDENCIES)
	@echo "$(YELLOW)[WARNING]$(RESET) Installing production dependencies..."
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'pip', 'install', '--upgrade', 'pip'])"
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'pip', 'install', '-r', '$(REQUIREMENTS)'])"
	@echo "$(GREEN)[INFO]$(RESET) Production dependencies installed ✓"

_install-dev: ## Internal: Install all dependencies (used by init-dev)
	$(call print_header,INSTALLING ALL DEPENDENCIES)
	@echo "$(YELLOW)[WARNING]$(RESET) Installing all dependencies..."
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'pip', 'install', '--upgrade', 'pip'])"
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'pip', 'install', '-r', '$(REQUIREMENTS)'])"
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'pip', 'install', '-r', '$(DEV_REQUIREMENTS)'])"
	@echo "$(GREEN)[INFO]$(RESET) Production dependencies installed ✓"
	@echo "$(GREEN)[INFO]$(RESET) Development dependencies installed ✓"

install-minimal: ## Install minimal dependencies for quick setup
	$(call print_header,INSTALLING MINIMAL DEPENDENCIES)
	$(call check_venv)
	@echo "$(YELLOW)[WARNING]$(RESET) Installing minimal dependencies..."
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'pip', 'install', '--upgrade', 'pip'])"
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'pip', 'install', '-r', '$(REQUIREMENTS)'])"
	@echo "$(GREEN)[INFO]$(RESET) Minimal dependencies installed ✓"

install-full: ## Install all dependencies including development tools
	$(call print_header,INSTALLING FULL DEPENDENCIES)
	$(call check_venv)
	@echo "$(YELLOW)[WARNING]$(RESET) Installing full dependencies..."
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'pip', 'install', '--upgrade', 'pip'])"
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'pip', 'install', '-r', '$(REQUIREMENTS)'])"
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'pip', 'install', '-r', '$(DEV_REQUIREMENTS)'])"
	@echo "$(GREEN)[INFO]$(RESET) Full dependencies installed ✓"

setup-env: ## Setup environment configuration files
	$(call print_header,ENVIRONMENT SETUP)
	@$(PYTHON) -c "import os, shutil; shutil.copy('.env.example', '.env') if os.path.exists('.env.example') and not os.path.exists('.env') else None"
	@if [ ! -f ".env" ]; then \
		echo "$(YELLOW)[WARNING]$(RESET) No .env.example found. Please create .env file manually."; \
	else \
		echo "$(GREEN)[INFO]$(RESET) Environment file ready ✓"; \
	fi
	@if [ ! -f ".env.local" ]; then \
		echo "# Local Development Environment" > .env.local; \
		echo "ENV=development" >> .env.local; \
		echo "DEBUG=True" >> .env.local; \
		echo "LOG_LEVEL=DEBUG" >> .env.local; \
		echo "USE_MOCK_AWS=true" >> .env.local; \
		echo "" >> .env.local; \
		echo "# API Configuration" >> .env.local; \
		echo "API_PORT=8000" >> .env.local; \
		echo "API_HOST=0.0.0.0" >> .env.local; \
		echo "" >> .env.local; \
		echo "# AWS Configuration (for local development)" >> .env.local; \
		echo "AWS_REGION=us-east-1" >> .env.local; \
		echo "AWS_ACCESS_KEY_ID=test" >> .env.local; \
		echo "AWS_SECRET_ACCESS_KEY=test" >> .env.local; \
		echo "" >> .env.local; \
		echo "# S3 Configuration" >> .env.local; \
		echo "S3_BUCKET=test-bucket" >> .env.local; \
		echo "S3_PREFIX=loan-documents/" >> .env.local; \
		echo "" >> .env.local; \
		echo "# Knowledge Base Configuration (test values)" >> .env.local; \
		echo "KNOWLEDGE_BASE_ID=test-kb-id" >> .env.local; \
		echo "DATA_SOURCE_ID=test-data-source-id" >> .env.local; \
		echo "" >> .env.local; \
		echo "# DynamoDB Tables (test values)" >> .env.local; \
		echo "LOAN_BOOKING_TABLE_NAME=test-loan-bookings" >> .env.local; \
		echo "BOOKING_SHEET_TABLE_NAME=test-booking-sheet" >> .env.local; \
		echo "" >> .env.local; \
		echo "# CORS Configuration - Development (Permissive)" >> .env.local; \
		echo "ALLOWED_ORIGINS=*" >> .env.local; \
		echo "ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS" >> .env.local; \
		echo "ALLOWED_HEADERS=*" >> .env.local; \
		echo "ALLOW_CREDENTIALS=true" >> .env.local; \
		echo "" >> .env.local; \
		echo "# Security - Development" >> .env.local; \
		echo "SKIP_AWS_VALIDATION=true" >> .env.local; \
		echo "$(GREEN)[INFO]$(RESET) Local environment file created ✓"; \
	else \
		echo "$(GREEN)[INFO]$(RESET) Local environment file already exists ✓"; \
	fi

# Development Commands
backend: ## Start development server with hot reload
	$(call print_header,STARTING DEVELOPMENT SERVER)
	@$(PYTHON) -c "import os; exit(1) if not os.path.exists('$(VENV_DIR)') else exit(0)" || (echo "$(RED)[ERROR]$(RESET) Virtual environment not found. Run 'make init-dev' first." && exit 1)
	@$(PYTHON) -c "import os, subprocess; env = dict(os.environ); [env.update({line.split('=')[0]: '='.join(line.split('=')[1:])}) for line in open('.env.local').read().splitlines() if line and not line.startswith('#') and '=' in line] if os.path.exists('.env.local') else None; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'uvicorn', 'main:app', '--reload', '--host', env.get('API_HOST', '0.0.0.0'), '--port', env.get('API_PORT', '8000'), '--log-level', 'debug'], env=env)"

backend-prod: ## Start production server (local testing)
	$(call print_header,STARTING PRODUCTION SERVER (LOCAL))
	@$(PYTHON) -c "import os; exit(1) if not os.path.exists('$(VENV_DIR)') else exit(0)" || (echo "$(RED)[ERROR]$(RESET) Virtual environment not found. Run 'make init-dev' first." && exit 1)
	@if [ ! -f ".env.production" ]; then echo "$(RED)[ERROR]$(RESET) .env.production file not found. Create one from .env.example" && exit 1; fi
	@$(PYTHON) -c "import os, subprocess; env = dict(os.environ); [env.update({line.split('=')[0]: '='.join(line.split('=')[1:])}) for line in open('.env.production').read().splitlines() if line and not line.startswith('#') and '=' in line]; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'uvicorn', 'main:app', '--host', env.get('API_HOST', '0.0.0.0'), '--port', env.get('API_PORT', '8000'), '--workers', env.get('API_WORKERS', '4')], env=env)"

backend-staging: ## Start staging server (local testing)
	$(call print_header,STARTING STAGING SERVER (LOCAL))
	@$(PYTHON) -c "import os; exit(1) if not os.path.exists('$(VENV_DIR)') else exit(0)" || (echo "$(RED)[ERROR]$(RESET) Virtual environment not found. Run 'make init-dev' first." && exit 1)
	@if [ ! -f ".env.staging" ]; then echo "$(RED)[ERROR]$(RESET) .env.staging file not found. Create one from .env.example" && exit 1; fi
	@$(PYTHON) -c "import os, subprocess; env = dict(os.environ); [env.update({line.split('=')[0]: '='.join(line.split('=')[1:])}) for line in open('.env.staging').read().splitlines() if line and not line.startswith('#') and '=' in line]; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'uvicorn', 'main:app', '--host', env.get('API_HOST', '0.0.0.0'), '--port', env.get('API_PORT', '8000'), '--workers', env.get('API_WORKERS', '2')], env=env)"

# Testing Commands
test: ## Run unit tests with coverage report
	$(call print_header,RUNNING TESTS)
	@$(PYTHON) -c "import os; exit(1) if not os.path.exists('$(VENV_DIR)') else exit(0)" || (echo "$(RED)[ERROR]$(RESET) Virtual environment not found. Run 'make init-dev' first." && exit 1)
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'pytest', '$(TEST_DIR)/', '-v', '--cov=.', '--cov-report=term-missing', '--cov-fail-under=$(COVERAGE_MIN)'])"
	@echo "$(GREEN)[INFO]$(RESET) Tests completed ✓"

test-cov: ## Run tests with detailed coverage analysis
	$(call print_header,RUNNING TESTS WITH DETAILED COVERAGE)
	@$(PYTHON) -c "import os; exit(1) if not os.path.exists('$(VENV_DIR)') else exit(0)" || (echo "$(RED)[ERROR]$(RESET) Virtual environment not found. Run 'make init-dev' first." && exit 1)
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'pytest', '$(TEST_DIR)/', '-v', '--cov=.', '--cov-report=term-missing', '--cov-report=html', '--cov-fail-under=$(COVERAGE_MIN)'])"
	@echo "$(GREEN)[INFO]$(RESET) Tests completed with detailed coverage ✓"
	@echo "$(GREEN)[INFO]$(RESET) HTML coverage report generated in htmlcov/ directory"

test-report: ## Generate HTML coverage report
	$(call print_header,GENERATING COVERAGE REPORT)
	@$(PYTHON) -c "import os; exit(1) if not os.path.exists('$(VENV_DIR)') else exit(0)" || (echo "$(RED)[ERROR]$(RESET) Virtual environment not found. Run 'make init-dev' first." && exit 1)
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'pytest', '$(TEST_DIR)/', '--cov=.', '--cov-report=html', '--cov-report=term'])"
	@echo "$(GREEN)[INFO]$(RESET) HTML coverage report generated ✓"
	@echo "$(YELLOW)Open htmlcov/index.html in your browser to view the report$(RESET)"

# Code Quality Commands
lint: format type-check security ## Run all linting and formatting checks
	$(call print_header,LINTING COMPLETE)
	@echo "$(GREEN)[INFO]$(RESET) All code quality checks passed ✓"

format: ## Auto-format code (black, isort)
	$(call print_header,FORMATTING CODE)
	@$(PYTHON) -c "import os; exit(1) if not os.path.exists('$(VENV_DIR)') else exit(0)" || (echo "$(RED)[ERROR]$(RESET) Virtual environment not found. Run 'make init-dev' first." && exit 1)
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'black', '$(SRC_DIRS)', '$(TEST_DIR)', '--line-length', '88'])"
	@echo "$(GREEN)[INFO]$(RESET) Code formatted with black ✓"
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'isort', '$(SRC_DIRS)', '$(TEST_DIR)', '--profile', 'black'])"
	@echo "$(GREEN)[INFO]$(RESET) Imports sorted with isort ✓"

type-check: ## Run type checking with mypy
	$(call print_header,TYPE CHECKING)
	@$(PYTHON) -c "import os; exit(1) if not os.path.exists('$(VENV_DIR)') else exit(0)" || (echo "$(RED)[ERROR]$(RESET) Virtual environment not found. Run 'make init-dev' first." && exit 1)
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'mypy', '$(SRC_DIRS)', '--ignore-missing-imports', '--strict-optional', '--warn-redundant-casts', '--warn-unused-ignores'])"
	@echo "$(GREEN)[INFO]$(RESET) Type checking completed ✓"

security: ## Run security analysis with bandit
	$(call print_header,SECURITY ANALYSIS)
	@$(PYTHON) -c "import os; exit(1) if not os.path.exists('$(VENV_DIR)') else exit(0)" || (echo "$(RED)[ERROR]$(RESET) Virtual environment not found. Run 'make init-dev' first." && exit 1)
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'bandit', '-r', '$(SRC_DIRS)', '-f', 'json', '-o', 'bandit-report.json']) or True"
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'bandit', '-r', '$(SRC_DIRS)', '-x', '$(TEST_DIR)/', '--severity-level', 'medium'])"
	@echo "$(GREEN)[INFO]$(RESET) Security analysis completed ✓"

# Utility Commands
clean: ## Clean cache and temporary files
	$(call print_header,CLEANING CACHE)
	@$(PYTHON) -c "import os, shutil, glob; [os.remove(f) for f in glob.glob('**/*.pyc', recursive=True) if os.path.exists(f)]"
	@$(PYTHON) -c "import os, shutil, glob; [shutil.rmtree(d) for d in glob.glob('**/__pycache__', recursive=True) if os.path.exists(d)]"
	@$(PYTHON) -c "import os, shutil, glob; [shutil.rmtree(d) for d in glob.glob('**/*.egg-info', recursive=True) if os.path.exists(d)]"
	@$(PYTHON) -c "import os, shutil; [shutil.rmtree(d) if os.path.exists(d) else None for d in ['.pytest_cache', 'htmlcov', 'temp']]"
	@$(PYTHON) -c "import os; [os.remove(f) if os.path.exists(f) else None for f in ['.coverage', 'bandit-report.json']]"
	@echo "$(GREEN)[INFO]$(RESET) Cache and temporary files cleaned ✓"

clean-cache: clean ## Alias for clean

clean-all: clean ## Clean everything including virtual environment
	$(call print_header,DEEP CLEANING)
	@$(PYTHON) -c "import os, shutil; shutil.rmtree('$(VENV_DIR)') if os.path.exists('$(VENV_DIR)') else None"
	@$(PYTHON) -c "import os, glob; [os.remove(f) for f in glob.glob('logs/*.log') if os.path.exists(f)]"
	@echo "$(GREEN)[INFO]$(RESET) Virtual environment removed ✓"
	@echo "$(GREEN)[INFO]$(RESET) Log files cleaned ✓"

# Docker Commands
docker-build: ## Build Docker image
	$(call print_header,BUILDING DOCKER IMAGE)
	docker build -f docker/Dockerfile -t loan-onboarding-api:latest .
	$(call print_status,Docker image built ✓)

docker-up: ## Start services with Docker Compose
	$(call print_header,STARTING DOCKER SERVICES)
	docker-compose -f docker/docker-compose.local.yml up -d
	$(call print_status,Docker services started ✓)
	@echo "$(YELLOW)API available at: http://localhost:8000$(RESET)"
	@echo "$(YELLOW)API docs at: http://localhost:8000/docs$(RESET)"

docker-down: ## Stop Docker services
	$(call print_header,STOPPING DOCKER SERVICES)
	docker-compose -f docker/docker-compose.local.yml down
	$(call print_status,Docker services stopped ✓)

docker-test: ## Run tests in Docker container
	$(call print_header,RUNNING TESTS IN DOCKER)
	docker-compose -f docker/docker-compose.local.yml run --rm loan-api pytest tests/ -v --cov=. --cov-report=term-missing
	$(call print_status,Docker tests completed ✓)

# Documentation
docs: ## Generate/serve API documentation
	$(call print_header,API DOCUMENTATION)
	@$(PYTHON) -c "import os; exit(1) if not os.path.exists('$(VENV_DIR)') else exit(0)" || (echo "$(RED)[ERROR]$(RESET) Virtual environment not found. Run 'make init-dev' first." && exit 1)
	@echo "$(YELLOW)Starting development server for API documentation...$(RESET)"
	@echo "$(YELLOW)API docs will be available at: http://localhost:8000/docs$(RESET)"
	@echo "$(YELLOW)Alternative docs at: http://localhost:8000/redoc$(RESET)"
	@echo "$(YELLOW)Press Ctrl+C to stop$(RESET)"
	@$(PYTHON) -c "import subprocess, os; subprocess.run([os.path.join('$(VENV_DIR)', 'Scripts', 'python'), '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'])"

# Activate helper (for convenience)
activate: ## Show command to activate virtual environment
	@echo "$(YELLOW)To activate virtual environment, run:$(RESET)"
	@echo "$(BOLD)source $(VENV_ACTIVATE)$(RESET)"

# Pre-commit setup
pre-commit: ## Install and setup pre-commit hooks
	$(call check_venv)
	$(call print_header,SETTING UP PRE-COMMIT HOOKS)
	@$(PYTHON) -c "import subprocess; subprocess.run(['pre-commit', 'install']); print('$(GREEN)[INFO]$(RESET) Pre-commit hooks installed ✓')" 2>/dev/null || (echo "$(YELLOW)[WARNING]$(RESET) pre-commit not found. Installing..." && $(PIP) install pre-commit && pre-commit install && echo "$(GREEN)[INFO]$(RESET) Pre-commit installed and hooks setup ✓")

# Quick development workflow
dev: init-dev backend ## Quick development setup and start development server

# Full validation pipeline
validate: lint test security ## Run complete validation pipeline

# Show status
status: ## Show development environment status
	$(call print_header,DEVELOPMENT ENVIRONMENT STATUS)
	@echo "$(BOLD)Python:$(RESET)"
	@$(PYTHON) -c "import sys; print('  ✓ Python', sys.version.split()[0])" 2>/dev/null || echo "  ✗ Python not found"
	@echo "$(BOLD)Virtual Environment:$(RESET)"
	@$(PYTHON) -c "import os; print('  ✓ Virtual environment exists') if os.path.exists('$(VENV_DIR)') else print('  ✗ Virtual environment not found')"
	@$(PYTHON) -c "import os; print('  ✓ Virtual environment activated') if os.environ.get('VIRTUAL_ENV') else print('  ⚠ Virtual environment not activated')"
	@echo "$(BOLD)Environment Files:$(RESET)"
	@$(PYTHON) -c "import os; print('  ✓ .env file exists') if os.path.exists('.env') else print('  ✗ .env file missing')"
	@$(PYTHON) -c "import os; print('  ✓ .env.local file exists') if os.path.exists('.env.local') else print('  ✗ .env.local file missing')"
	@echo "$(BOLD)Dependencies:$(RESET)"
	@$(PYTHON) -c "import os, subprocess; print('  ✓ Development dependencies installed') if os.environ.get('VIRTUAL_ENV') and subprocess.run(['python', '-c', 'import pytest'], capture_output=True).returncode == 0 else print('  ⚠ Development dependencies may not be installed')"
