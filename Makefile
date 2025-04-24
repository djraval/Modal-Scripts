.PHONY: setup scrape clean

VENV_DIR := .venv
REQUIREMENTS := requirements.txt
SCRAPER_SCRIPT := modal-dev-ref/ref_scraper.py

# Default Python command (can be overridden via environment or command line if needed)
PYTHON_CMD ?= python

# Default to Unix paths
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip
VENV_UV := $(VENV_DIR)/bin/uv
RM_CMD := rm -rf $(VENV_DIR)

# Override for Windows
ifeq ($(OS),Windows_NT)
    VENV_PYTHON := $(VENV_DIR)\Scripts\python.exe
    VENV_PIP := $(VENV_DIR)\Scripts\pip.exe
    VENV_UV := $(VENV_DIR)\Scripts\uv.exe
    RM_CMD := rmdir /s /q $(VENV_DIR) 2> nul || exit 0 # Suppress error if dir doesn't exist
endif

setup:
	@echo "--- Ensuring virtual environment '$(VENV_DIR)' ---"
	$(PYTHON_CMD) -m venv $(VENV_DIR)
	@echo "--- Installing/updating dependencies via pip and uv ---"
	"$(VENV_PYTHON)" -m pip install --upgrade pip uv
	"$(VENV_PYTHON)" -m uv pip install -r $(REQUIREMENTS)
	@echo "--- Setup complete ---"

scrape: setup
	@echo "--- Running scraper script ---"
	"$(VENV_PYTHON)" $(SCRAPER_SCRIPT)

clean:
	@echo "--- Removing virtual environment $(VENV_DIR) ---"
	@$(RM_CMD)
	@echo "--- Clean complete ---"
