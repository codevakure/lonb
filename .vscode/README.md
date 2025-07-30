# VS Code Team Development Setup

This directory contains team-shared VS Code configuration for the Loan Onboarding API project.

## Files Included

### settings.json
Comprehensive team development settings including:
- **Python Development**: Black formatting, type checking, testing configuration
- **Code Quality**: Linting, import sorting, security scanning
- **Testing**: Pytest integration with coverage reporting
- **GitHub Copilot**: AI-powered code assistance with project-specific instructions
- **File Associations**: YAML, JSON, and Python file handling
- **Terminal**: Integrated terminal configuration for Windows/PowerShell

### extensions.json
Recommended extensions for this project:
- **Core Python**: python, black-formatter, isort, mypy, pylint
- **Testing**: jupyter, coverage-gutters
- **Cloud & Docker**: azure-repos, vscode-docker
- **AI**: GitHub Copilot and Copilot Chat
- **Productivity**: path-intellisense, todo-tree, bookmarks

### tasks.json
Pre-configured tasks for common development workflows:
- Start FastAPI development server
- Run tests with coverage
- Code formatting (Black) and linting
- Docker operations
- Security scanning

### launch.json
Debug configurations for:
- FastAPI application debugging
- Running individual Python files
- Environment-specific debugging

## Getting Started

1. **Install Recommended Extensions**
   - VS Code will prompt you to install recommended extensions
   - Or manually install from the Extensions panel

2. **Open the Project**
   ```bash
   cd c:\loan-onboarding\api
   code .
   ```

3. **Start Development**
   - Use `Ctrl+Shift+P` → "Tasks: Run Task" → "Start FastAPI Development Server"
   - Or use the debug configuration "FastAPI Development Server"

## Key Features

### Automatic Formatting
- **Black**: Formats Python code on save
- **isort**: Sorts imports automatically
- **Line length**: 88 characters (Black standard)

### Testing Integration
- **Pytest**: Integrated test runner
- **Coverage**: Automatic coverage reporting
- **Test discovery**: Auto-detect test files

### Code Quality
- **MyPy**: Type checking enabled
- **Pylint**: Linting with project-specific rules
- **Security**: Bandit integration for security scanning

### GitHub Copilot Setup
- Pre-configured with project-specific instructions
- Understands Texas Capital standards architecture
- Knows about loan booking, boarding sheet, and product domains

## Environment Variables

The configuration expects these environment variables:
- `ENV`: development/test/production
- `DEBUG`: True/False
- `LOG_LEVEL`: DEBUG/INFO/WARNING/ERROR

## Troubleshooting

### Python Extension Issues
If you see "type python not recognized" errors in launch.json:
1. Install the Python extension (`ms-python.python`)
2. Reload VS Code
3. The launch configurations will work properly

### Formatting Not Working
1. Ensure Black formatter extension is installed
2. Check Python interpreter is selected (bottom status bar)
3. Verify settings.json has proper formatting configuration

### Tasks Not Running
1. Ensure you're in the correct workspace folder
2. Check that required dependencies are installed (`pip install -r requirements-dev.txt`)
3. Verify terminal is using correct Python environment

## Customization

### Personal Settings
Create user-specific files (these are git-ignored):
- `.vscode/settings.json.user`
- `.vscode/launch.json.user`

### Project Settings
Modify team settings by editing the main configuration files.
All team members will get the updates.

## File Structure
```
.vscode/
├── settings.json      # Team development settings
├── extensions.json    # Recommended extensions
├── tasks.json        # Build and development tasks  
├── launch.json       # Debug configurations
└── README.md         # This file
```

## Best Practices

1. **Keep team settings minimal**: Only include project-essential configuration
2. **Use extensions.json**: Let VS Code handle extension recommendations
3. **Document changes**: Update this README when modifying configurations
4. **Test configurations**: Verify settings work on different team member machines

## Support

For VS Code configuration issues:
1. Check the VS Code output panel for error messages
2. Verify all recommended extensions are installed
3. Ensure Python environment is properly configured
4. Review this README for common solutions

---

**Note**: These settings are designed for the Texas Capital Loan Onboarding API project and follow enterprise development standards with comprehensive tooling integration.
