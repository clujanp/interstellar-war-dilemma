# python-template
Template for Python repos

## Config repository
### set repository variables
  - PYTHON_VERSION
  - SRC_FOLDER
  - TESTS_FOLDER
  - COV_PERCENT
  - PYLINT_SCORE
  - REQUIREMENTS_DEV
  - REQUIREMENTS_PROD
  - STAGING_TF_BACKEND_AWS_REGION
  - STAGING_TF_STATE_BUCKET
  - STAGING_TF_STATE_KEY
  - PRODUCTION_TF_BACKEND_AWS_REGION
  - PRODUCTION_TF_STATE_BUCKET
  - PRODUCTION_TF_STATE_KEY

### available pre-build
  - GitHub Actions: CI for commits, pre-CD for PRs, CD for merges
  - .vscode settings: IDE status bar color
  - App structure: Hexagonal architectur:
    - Adapters
    - Core
    - Domain
    - Models
    - Services
    - Use cases
    - Infrastructure
    - logging
    - Utils
  - Config: for requirements and environment variables
  - Docker: for local development
  - Terraform: for staging and production environments
  - Tests: for unit and integration tests
  - Linting: for code quality qith pylint
  - Coverage: for code coverage with pytest-cov
  - CURP: Common Utilities for Python Repos script

> [!NOTE]
> Enjoi it!