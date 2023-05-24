# py-client-integration-tests
Integration tests using python sdk

### Instructions
1. Checkout repo and `cd py-client-integration-tests` to change to project root 
2. Install [poetry](https://python-poetry.org/docs/#installation)
3. `poetry install` to install dependencies
4. `poetry shell`to activate virtual env. [Read here](https://python-poetry.org/docs/basic-usage/#activating-the-virtual-environment) if you run into issues.
5. Copy`.env.example`file to`.env.dev`and add your Tigris secrets to the new `.env.dev` file.
6. `poetry run python -m unittest` to execute tests from cli, or run them from your IDE/Editor.