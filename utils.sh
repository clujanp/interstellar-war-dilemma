#!/bin/bash

# Project name and version
OWNER="Carlos Luján"
NAME="CURP"
VERSION="2.0.0"
DESCRIPTION="Common Utilities for Python Repositories."

SRC_FOLDER="app"
PYTHON_VERSION="3.11"
TEST_UNITARY_PATH="tests/unitary"
TEST_INTEGRATION_PATH="tests/integration"
REQUIREMENTS_PROD="config/requirements/production.txt"
REQUIREMENTS_DEV="config/requirements/development.txt"
ENTRY_POINT="app/main.py"
COV_PERCENT="80"
PYLINT_SCORE=8.0

DOCKER_APP="app"
DOCKER_AUTH="auth"
DOCKER_DYNAMODB="dynamodb-local"
DOCKER_COGNITO="cognito-local"
DOCKER_CONFIG_DYNAMODB="config-dynamodb"
DOCKER_CONFIG_COGNITO="config-cognito"

# Set global environment variable
set_env() {
    if [ "$1" == "--env:prod" ]; then
        env="prod"
    elif [ "$1" == "--env:dev" ]; then
        env="dev"
    elif [[ "$2" == "default-set-none" && "$1" != --env:* ]]; then
        env="none"
    else
        echo "enviroment $1 is no available"
        exit 1
    fi
}

# Create virtual environment
venv_create() {
    "python${PYTHON_VERSION}" -m venv "venv/$env"
}

# Activate virtual environment
venv_activate() {
    source "venv/$env/bin/activate"
}

# Get dependencies
get_dependencies() {
    venv_activate
    pip freeze
}

# Install dependencies
install_dependencies() {
    venv_activate
    pip install "$@"
    update_dependencies
}

run() {
    venv_activate
    export PYTHONPATH=$(pwd)
    python $ENTRY_POINT
}

# Set requirements by enviroment
set_requirements() {
    if [ "$env" == "prod" ]; then
        requirements=$REQUIREMENTS_PROD
    elif [ "$env" == "dev" ]; then
        requirements=$REQUIREMENTS_DEV
    else
        echo "enviroment $env is no available"
        exit 1
    fi
}

# Install requirements
install_requirements() {
    venv_activate
    if [ ! -f "$requirements" ]; then
        echo "File $requirements does not exist, will be create."
        touch "$requirements"
    fi
    pip install -r "$requirements"
    update_dependencies
}

# Uninstall dependencies
uninstall_dependencies() {
    venv_activate
    pip uninstall "$@"
    update_dependencies
}

# Update dependencies
update_dependencies() {
    venv_activate
    set_requirements
    pip freeze > $requirements
}

# Install pylint
install_lint() {
    venv_activate
    pip install pylint
}

# Run tests with coverage
cov() {
    venv_activate
    pytest --cov=$SRC_FOLDER/ $TEST_UNITARY_PATH/ --cov-fail-under=$COV_PERCENT  --cov-report html
}

# Run tests with coverage
integration() {
    venv_activate
    pytest -vv --tb=short $TEST_INTEGRATION_PATH
}

# Run tests
test() {
    venv_activate
    if [ -n "$@" ]; then
        pytest -vv --tb=short $SRC_FOLDER/ $TEST_UNITARY_PATH/ "$@"
    else
        pytest -vv --tb=short --cov=$SRC_FOLDER/ $TEST_UNITARY_PATH/ --cov-fail-under=$COV_PERCENT
    fi
}

# Run tests with logs
test_log() {
    clear
    venv_activate
    if [ -n "$@" ]; then
        pytest -o log_cli=true -vv --tb=short $TEST_UNITARY_PATH/ "$@"
    else
        pytest -o log_cli=true -vv --tb=short --cov=$SRC_FOLDER/ $TEST_UNITARY_PATH/ --cov-fail-under=$COV_PERCENT
    fi
}

# Run lint
lint() {
    venv_activate
    pylint $SRC_FOLDER --fail-under=$PYLINT_SCORE --output-format=text -r n
}

# Run Python REPL
repl() {
    venv_activate
    python
}

# Generate lint report
lint_report() {
    venv_activate
    pylint $SRC_FOLDER --fail-under=$PYLINT_SCORE > pylint_report.json 2>pylint_errors.log
    if [ $? != 0 ]; then
        echo "!!!Pylint score is below $PYLINT_SCORE. Check pylint_errors.log for details."
        exit 1
    fi
    pylint-json2html -o pylint_report.html pylint_report.json
    exit 0
}

# Clean compiled files
clean() {
    find $SRC_FOLDER -name '*.pyc' -delete
    find $SRC_FOLDER -name '__pycache__' -type d -exec rm -r {} +
}

# Install all (alias for preparing environment)
install_all() {
    venv_create
    venv_activate
    set_requirements
    install_requirements
    if [ "$env" != "dev" ]; then
        env="dev"
        venv_create
        venv_activate
        set_requirements
        install_requirements
    fi
    if [ "$env" == "dev" ]; then
        install_lint
    fi
}

# Add __init__.py recursively
add_init_files() {
    echo "Adding __init__.py files recursively in $SRC_FOLDER/"
    find "$SRC_FOLDER" -type d ! -exec test -e '{}/__init__.py' \; -exec touch '{}/__init__.py' \;
    echo "__init__.py files added where missing."
}

# Show help
help() {
    echo "$NAME: V$VERSION Powered by $OWNER."
    echo "$DESCRIPTION"
    echo ""
    echo "  Usage: $0 <action> [-<action options>] [--env:<prod|dev>] [<args>]"
    echo ""
    echo "  actions:"
    echo "  -- common actions --"
    echo "    run                                       Run application"
    echo "    test                                      Run suite tests"
    echo "  -- unitests --"
    echo "    tests                                     Run all tests unitary and integration"
    echo "    unit [test.py]                            Run unitary tests"
    echo "    unit -log [test.py]                       Run unitary tests with logs"
    echo "    integration                               Run integration tests"
    echo "    cov                                       Run tests with coverage"
    echo "    lint                                      Run lint"
    echo "    lint -report                              Generate lint report"
    echo "  -- libs manage --"
    echo "    i                                         Prepare environment local"
    echo "    libs                                      Get dependencies"
    echo "    libs -i [lib1, lib2, ...]                 Install dependencies"
    echo "    libs -x [lib1, lib2, ...]                 Uninstall dependencies"
    echo "    libs -u                                   Update dependencies"
    echo "  -- venv manage --"
    echo "    venv --create                             Create virtual environment"
    echo "    lint --install                            Install pylint"
    echo "  -- others --"
    echo "    repl                                      Run Python REPL"
    echo "    clean                                     Clean compiled files"
    echo "    add-init                                  Add __init__.py files recursively"
    echo "    help                                      Show this help message"
    echo ""
    echo "  environments:"
    echo "    --env:prod                                Production environment"
    echo "    --env:dev                                 Development environment"
}

# Main command
case "$1" in
    i)
        set_env "${2:---env:dev}"
        install_all
        ;;
    run)
        set_env "${2:---env:dev}"
        run
        ;;
    venv)
        case "$2" in
            --create)
                set_env "${3:---env:dev}"
                venv_create
                ;;
            *)
                help
                ;;
        esac
        ;;
    libs)
        case "$2" in
            --env:prod|--env:actions|--env:dev)
                set_env "${2:---env:dev}"
                get_dependencies
                ;;
            -i)
                set_env $3 "default-set-none"
                # when enviro is set by default
                if [ $env == "none" ]; then
                    env="dev"
                    shift 2
                else
                    shift 3
                fi
                install_dependencies "$@"
                ;;
            -x)
                set_env $3 "default-set-none"
                # when enviro is set by default
                if [ $env == "none" ]; then
                    env="dev"
                    shift 2
                else
                    shift 3
                fi
                uninstall_dependencies "$@"
                ;;
            -u)
                set_env "${3:---env:dev}"
                update_dependencies
                ;;
            *)
                help
                ;;
        esac
        ;;
    lint)
        case "$2" in
            -install)
                env="dev"
                install_lint
                ;;
            -report)
                env="dev"
                lint_report
                ;;
            *)
                env="dev"
                lint
                ;;
        esac
        ;;
    cov)
        if [[ "$2" == --env:prod || "$2" == --env:actions || "$2" == --env:dev ]]; then
            set_env "$2"
            cov
        else
            env="dev"
            cov
        fi
        ;;
    tests)
        if [[ "$2" == --env:prod || "$2" == --env:actions || "$2" == --env:dev ]]; then
            set_env "$2"
            echo "---- UNITARY TESTS ---------------------------------------------"
            cov
            echo "---- INTEGRATION TESTS -----------------------------------------"
            integration
        else
            env="dev"
            echo "---- UNITARY TESTS ---------------------------------------------"
            cov
            echo "---- INTEGRATION TESTS -----------------------------------------"
            integration
        fi
        ;;
    integration)
        if [[ "$2" == --env:prod || "$2" == --env:actions || "$2" == --env:dev ]]; then
            set_env "$2"
            integration
        else
            env="dev"
            integration
        fi
        ;;
    unit)
        case "$2" in
            --env:prod|--env:actions|--env:dev)
                set_env "$2"
                shift 2
                test "$@"
                ;;
            -log)
                set_env $3 "default-set-none"
                # when enviro is set by default
                if [ $env == "none" ]; then
                    env="dev"
                    shift 2
                else
                    shift 3
                fi
                test_log "$@"
                ;;
            *)
                env="dev"
                shift
                test "$@"
                ;;
        esac
        ;;
    docker)
        if [ "$2" == "-build" ]; then
            echo "Executing docker-compose up -d --build..."
            docker-compose up -d --build $DOCKER_DYNAMODB $DOCKER_COGNITO $DOCKER_CONFIG_COGNITO $DOCKER_CONFIG_DYNAMODB
            sleep 15
            docker-compose up -d --build $DOCKER_APP $DOCKER_AUTH
        else
            echo "Executing docker-compose up -d..."
            docker-compose up -d $DOCKER_DYNAMODB $DOCKER_COGNITO $DOCKER_CONFIG_COGNITO $DOCKER_CONFIG_DYNAMODB
            sleep 15
            docker-compose up -d $DOCKER_APP $DOCKER_AUTH
        fi
        ;;
    repl)
        case "$2" in
            --env:prod|--env:actions|--env:dev)
                set_env "$2"
                shift 2
                repl "$@"
                ;;
            *)
                shift
                env="dev"
                repl "$@"
                ;;
        esac
        ;;
    add-init)
        env="dev"
        add_init_files
        ;;
    clean)
        clean
        ;;
    help|*)
        help
        ;;
esac
