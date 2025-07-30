@echo off
REM Loan Onboarding API - Development Batch Script for Windows
REM This provides similar functionality to the Makefile for Windows users

setlocal enabledelayedexpansion

REM Variables
set PYTHON=python
set PIP=pip
set VENV_DIR=.venv
set REQUIREMENTS=requirements.txt
set DEV_REQUIREMENTS=requirements-dev.txt
set TEST_DIR=tests
set SRC_DIRS=api services utils config
set COVERAGE_MIN=85

REM Color codes for Windows
set RED=[31m
set GREEN=[32m
set YELLOW=[33m
set BLUE=[34m
set RESET=[0m

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="init" goto init
if "%1"=="backend" goto backend
if "%1"=="backend-dev" goto backend-dev
if "%1"=="backend-staging" goto backend-staging
if "%1"=="backend-prod" goto backend-prod
if "%1"=="test" goto test
if "%1"=="test-cov" goto test-cov
if "%1"=="test-report" goto test-report
if "%1"=="lint" goto lint
if "%1"=="format" goto format
if "%1"=="type-check" goto type-check
if "%1"=="security" goto security
if "%1"=="clean" goto clean
if "%1"=="clean-all" goto clean-all
if "%1"=="venv" goto venv
if "%1"=="install-dev" goto install-dev
if "%1"=="setup-env" goto setup-env
if "%1"=="env-validate" goto env-validate
if "%1"=="env-template" goto env-template
if "%1"=="env-copy" goto env-copy
if "%1"=="docker-build" goto docker-build
if "%1"=="docker-up" goto docker-up
if "%1"=="docker-down" goto docker-down
if "%1"=="docker-test" goto docker-test
if "%1"=="status" goto status
if "%1"=="validate" goto validate

echo Unknown command: %1
goto help

:help
echo %BLUE%Loan Onboarding API - Development Commands (Windows)%RESET%
echo.
echo %GREEN%Setup Commands:%RESET%
echo   make.bat init          Setup virtual environment, install dependencies, and configure environment
echo   make.bat venv          Create virtual environment only
echo   make.bat install-dev   Install development dependencies
echo   make.bat setup-env     Setup environment configuration files
echo.
echo %GREEN%Development Commands:%RESET%
echo   make.bat backend       Start development server with hot reload (uses .env.local)
echo   make.bat backend-dev   Start development server using .env.development
echo   make.bat backend-staging Start staging server using .env.staging
echo   make.bat backend-prod  Start production server using .env.production
echo   make.bat test          Run unit tests with coverage report
echo   make.bat test-cov      Run tests with detailed coverage analysis
echo   make.bat test-report   Generate HTML coverage report
echo.
echo %GREEN%Environment Commands:%RESET%
echo   make.bat env-validate  Validate current environment configuration
echo   make.bat env-template  Show environment variable template
echo   make.bat env-copy      Copy environment files for different environments
echo.
echo %GREEN%Code Quality Commands:%RESET%
echo   make.bat lint          Run all linting and formatting checks
echo   make.bat format        Auto-format code (black, isort)
echo   make.bat type-check    Run type checking with mypy
echo   make.bat security      Run security analysis with bandit
echo.
echo %GREEN%Utility Commands:%RESET%
echo   make.bat clean         Clean cache and temporary files
echo   make.bat clean-all     Clean everything including virtual environment
echo   make.bat status        Show development environment status
echo   make.bat validate      Run complete validation pipeline
echo.
echo %GREEN%Docker Commands:%RESET%
echo   make.bat docker-build  Build Docker image
echo   make.bat docker-up     Start services with Docker Compose
echo   make.bat docker-down   Stop Docker services
echo   make.bat docker-test   Run tests in Docker container
echo.
goto end

:init
echo %BLUE%[SETUP] Complete initialization%RESET%
call :check-python
if errorlevel 1 goto end
call :create-venv
call :install-dependencies
call :setup-environment
echo.
echo %GREEN%Setup completed successfully!%RESET%
echo.
echo Next steps:
echo 1. Activate virtual environment: %VENV_DIR%\Scripts\activate
echo 2. Update .env file with your configuration
echo 3. Start development server: make.bat backend
echo 4. Run tests: make.bat test
goto end

:venv
call :check-python
if errorlevel 1 goto end
call :create-venv
goto end

:install-dev
call :check-venv
if errorlevel 1 goto end
call :install-dependencies
goto end

:setup-env
call :setup-environment
goto end

:backend
call :check-venv
if errorlevel 1 goto end
echo %BLUE%[STARTING] Development Server%RESET%
if exist .env.local (
    for /f "tokens=1,2 delims==" %%a in ('type .env.local ^| findstr /v "^#"') do set %%a=%%b
)
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
goto end

:test
call :check-venv
if errorlevel 1 goto end
echo %BLUE%[RUNNING] Tests%RESET%
pytest %TEST_DIR%/ -v --cov=. --cov-report=term-missing --cov-fail-under=%COVERAGE_MIN%
echo %GREEN%Tests completed%RESET%
goto end

:test-cov
call :check-venv
if errorlevel 1 goto end
echo %BLUE%[RUNNING] Tests with detailed coverage%RESET%
pytest %TEST_DIR%/ -v --cov=. --cov-report=term-missing --cov-report=html --cov-fail-under=%COVERAGE_MIN%
echo %GREEN%Tests completed with detailed coverage%RESET%
echo %YELLOW%HTML coverage report generated in htmlcov/ directory%RESET%
goto end

:test-report
call :check-venv
if errorlevel 1 goto end
echo %BLUE%[GENERATING] Coverage Report%RESET%
pytest %TEST_DIR%/ --cov=. --cov-report=html --cov-report=term
echo %GREEN%HTML coverage report generated%RESET%
echo %YELLOW%Open htmlcov\index.html in your browser to view the report%RESET%
goto end

:format
call :check-venv
if errorlevel 1 goto end
echo %BLUE%[FORMATTING] Code%RESET%
black %SRC_DIRS% %TEST_DIR% --line-length 88
echo %GREEN%Code formatted with black%RESET%
isort %SRC_DIRS% %TEST_DIR% --profile black
echo %GREEN%Imports sorted with isort%RESET%
goto end

:type-check
call :check-venv
if errorlevel 1 goto end
echo %BLUE%[TYPE CHECKING]%RESET%
mypy %SRC_DIRS% --ignore-missing-imports --strict-optional --warn-redundant-casts --warn-unused-ignores
echo %GREEN%Type checking completed%RESET%
goto end

:security
call :check-venv
if errorlevel 1 goto end
echo %BLUE%[SECURITY] Analysis%RESET%
bandit -r %SRC_DIRS% -f json -o bandit-report.json
bandit -r %SRC_DIRS% -x %TEST_DIR%/ --severity-level medium
echo %GREEN%Security analysis completed%RESET%
goto end

:lint
call :format
call :type-check
call :security
echo %BLUE%[LINTING] Complete%RESET%
echo %GREEN%All code quality checks passed%RESET%
goto end

:clean
echo %BLUE%[CLEANING] Cache and temporary files%RESET%
for /r . %%f in (*.pyc) do del "%%f" >nul 2>&1
for /d /r . %%d in (__pycache__) do rd /s /q "%%d" >nul 2>&1
for /d /r . %%d in (*.egg-info) do rd /s /q "%%d" >nul 2>&1
rd /s /q .pytest_cache >nul 2>&1
rd /s /q htmlcov >nul 2>&1
del .coverage >nul 2>&1
del bandit-report.json >nul 2>&1
rd /s /q temp >nul 2>&1
echo %GREEN%Cache and temporary files cleaned%RESET%
goto end

:clean-all
call :clean
echo %BLUE%[DEEP CLEANING]%RESET%
rd /s /q %VENV_DIR% >nul 2>&1
del logs\*.log >nul 2>&1
echo %GREEN%Virtual environment removed%RESET%
echo %GREEN%Log files cleaned%RESET%
goto end

:docker-build
echo %BLUE%[BUILDING] Docker Image%RESET%
docker build -f docker/Dockerfile -t loan-onboarding-api:latest .
echo %GREEN%Docker image built%RESET%
goto end

:docker-up
echo %BLUE%[STARTING] Docker Services%RESET%
docker-compose -f docker/docker-compose.local.yml up -d
echo %GREEN%Docker services started%RESET%
echo %YELLOW%API available at: http://localhost:8000%RESET%
echo %YELLOW%API docs at: http://localhost:8000/docs%RESET%
goto end

:docker-down
echo %BLUE%[STOPPING] Docker Services%RESET%
docker-compose -f docker/docker-compose.local.yml down
echo %GREEN%Docker services stopped%RESET%
goto end

:docker-test
echo %BLUE%[RUNNING] Tests in Docker%RESET%
docker-compose -f docker/docker-compose.local.yml run --rm loan-api pytest tests/ -v --cov=. --cov-report=term-missing
echo %GREEN%Docker tests completed%RESET%
goto end

:validate
call :lint
call :test
call :security
echo %GREEN%Complete validation pipeline finished%RESET%
goto end

:status
echo %BLUE%[STATUS] Development Environment%RESET%
echo.
echo Python:
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo   X Python not found
) else (
    echo   √ Python found
    %PYTHON% --version
)
echo.
echo Virtual Environment:
if exist %VENV_DIR% (
    echo   √ Virtual environment exists
    if defined VIRTUAL_ENV (
        echo   √ Virtual environment activated
    ) else (
        echo   ! Virtual environment not activated
    )
) else (
    echo   X Virtual environment not found
)
echo.
echo Environment Files:
if exist .env (
    echo   √ .env file exists
) else (
    echo   X .env file missing
)
if exist .env.local (
    echo   √ .env.local file exists
) else (
    echo   X .env.local file missing
)
goto end

REM Helper functions
:check-python
echo %BLUE%[CHECKING] Python%RESET%
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR] Python is not installed. Please install Python 3.11 or higher.%RESET%
    exit /b 1
)
echo %GREEN%Python found%RESET%
exit /b 0

:check-venv
if not defined VIRTUAL_ENV (
    echo %YELLOW%[WARNING] Virtual environment not activated. Run 'make.bat init' first or activate manually.%RESET%
    exit /b 1
)
exit /b 0

:create-venv
echo %BLUE%[CREATING] Virtual Environment%RESET%
if exist %VENV_DIR% (
    echo %YELLOW%Virtual environment already exists. Removing old one...%RESET%
    rd /s /q %VENV_DIR%
)
%PYTHON% -m venv %VENV_DIR%
echo %GREEN%Virtual environment created%RESET%
echo %YELLOW%To activate: %VENV_DIR%\Scripts\activate%RESET%
exit /b 0

:install-dependencies
echo %BLUE%[INSTALLING] Dependencies%RESET%
if not exist %VENV_DIR% (
    echo %RED%[ERROR] Virtual environment not found. Run 'make.bat venv' first.%RESET%
    exit /b 1
)
if not defined VIRTUAL_ENV (
    echo %YELLOW%Activating virtual environment...%RESET%
    call %VENV_DIR%\Scripts\activate
)
%PIP% install --upgrade pip
%PIP% install -r %REQUIREMENTS%
%PIP% install -r %DEV_REQUIREMENTS%
echo %GREEN%Production dependencies installed%RESET%
echo %GREEN%Development dependencies installed%RESET%
exit /b 0

:setup-environment
echo %BLUE%[SETTING UP] Environment%RESET%
if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo %GREEN%Environment file created from example%RESET%
        echo %YELLOW%Please update .env file with your specific configuration.%RESET%
    ) else (
        echo %YELLOW%No .env.example found. Please create .env file manually.%RESET%
    )
) else (
    echo %GREEN%Environment file already exists%RESET%
)

if not exist .env.local (
    echo # Local Development Environment > .env.local
    echo ENV=development >> .env.local
    echo DEBUG=True >> .env.local
    echo LOG_LEVEL=DEBUG >> .env.local
    echo USE_MOCK_AWS=true >> .env.local
    echo. >> .env.local
    echo # API Configuration >> .env.local
    echo API_PORT=8000 >> .env.local
    echo API_HOST=0.0.0.0 >> .env.local
    echo. >> .env.local
    echo # AWS Configuration (for local development) >> .env.local
    echo AWS_REGION=us-east-1 >> .env.local
    echo AWS_ACCESS_KEY_ID=test >> .env.local
    echo AWS_SECRET_ACCESS_KEY=test >> .env.local
    echo. >> .env.local
    echo # S3 Configuration >> .env.local
    echo S3_BUCKET=test-bucket >> .env.local
    echo S3_PREFIX=loan-documents/ >> .env.local
    echo. >> .env.local
    echo # Knowledge Base Configuration (test values) >> .env.local
    echo KNOWLEDGE_BASE_ID=test-kb-id >> .env.local
    echo DATA_SOURCE_ID=test-data-source-id >> .env.local
    echo. >> .env.local
    echo # DynamoDB Tables (test values) >> .env.local
    echo LOAN_BOOKING_TABLE_NAME=test-loan-bookings >> .env.local
    echo BOOKING_SHEET_TABLE_NAME=test-booking-sheet >> .env.local
    echo. >> .env.local
    echo # CORS Configuration - Development (Permissive) >> .env.local
    echo ALLOWED_ORIGINS=* >> .env.local
    echo ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS >> .env.local
    echo ALLOWED_HEADERS=* >> .env.local
    echo ALLOW_CREDENTIALS=true >> .env.local
    echo. >> .env.local
    echo # Security - Development >> .env.local
    echo SKIP_AWS_VALIDATION=true >> .env.local
    echo %GREEN%Local environment file created%RESET%
) else (
    echo %GREEN%Local environment file already exists%RESET%
)

exit /b 0

:end
endlocal
