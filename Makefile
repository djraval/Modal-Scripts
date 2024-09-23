.PHONY: setup scrape

# Define the virtual environment directory
VENV_DIR := venv

# Setup target to create a virtual environment and install/update dependencies
setup:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Setting up virtual environment..."; \
		python3 -m venv $(VENV_DIR); \
	else \
		echo "Virtual environment already exists. Updating dependencies..."; \
	fi
	@echo "Activating virtual environment and installing/updating dependencies..."
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r modal-dev-ref/requirements.txt
	@echo "Setup complete!"

# Scrape target depends on setup and runs the scraper script
scrape: setup
	$(VENV_DIR)/bin/python modal-dev-ref/ref_scraper.py

# Prevent make from interpreting arguments as targets
%:
	@:
