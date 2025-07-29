# GitHub Copilot Configuration

This document explains the GitHub Copilot configuration for the Commercial Loan Service API.

## 📋 Overview

This workspace is configured with comprehensive GitHub Copilot instructions that ensure all generated code follows:
- ✅ Texas Capital OpenAPI standards
- ✅ Commercial loan service patterns
- ✅ Enterprise security requirements
- ✅ Production-ready coding practices

## 🔧 Configuration Files

### Core Instructions
- **`.github/copilot-instructions.md`** - Main instructions file with comprehensive guidelines
- **`standard-swagger-fragments.yaml`** - Texas Capital OpenAPI standards (referenced by Copilot)

### Specialized Instructions
- **`.github/instructions/api-development.instructions.md`** - API endpoint development guidelines
- **`.github/instructions/testing.instructions.md`** - Testing standards and practices
- **`.github/instructions/models.instructions.md`** - Data model and schema guidelines

### Prompt Templates
- **`.github/prompts/create-api-endpoint.prompt.md`** - Template for creating new API endpoints
- **`.github/prompts/security-review.prompt.md`** - Security review checklist
- **`.github/prompts/generate-tests.prompt.md`** - Comprehensive test generation

### VS Code Settings
- **`.vscode/settings.json`** - Copilot-specific settings and custom instructions

## 🚀 How to Use

### Automatic Instructions
Copilot automatically applies instructions from `.github/copilot-instructions.md` to all chat requests when the setting `github.copilot.chat.codeGeneration.useInstructionFiles` is enabled.

### Manual Instructions
You can manually attach specific instruction files:
1. Open Chat view in VS Code
2. Click "Add Context" > "Instructions"
3. Select the relevant `.instructions.md` file

### Prompt Templates
Use prompt templates for common tasks:
1. In Chat view, type `/` followed by prompt name
2. Example: `/create-api-endpoint`
3. Follow the prompts to provide required information

## 📖 Texas Capital Standards

All generated code follows Texas Capital OpenAPI standards:

### Required Headers
- `x-tc-request-id` - Unique request identifier
- `x-tc-correlation-id` - Cross-service correlation tracking  
- `tc-api-key` - API authentication key

### Standard Response Models
- **Success**: Use `SuccessModel` schema with proper status codes
- **Errors**: Use `ErrorModel` schema with detailed error information
- **Health**: Use `HealthCheckModel` for health endpoints

### API Design Principles
1. RESTful design with `/api/v1/` prefix
2. Comprehensive OpenAPI documentation
3. Input validation using Pydantic models
4. Proper error handling and logging
5. Security-first approach

## 🛡️ Security Focus

The configuration emphasizes security for financial services:
- Input validation and sanitization
- Authentication and authorization
- Audit logging with correlation IDs
- Sensitive data protection
- AWS security best practices

## 🧪 Testing Standards

Generated tests follow enterprise patterns:
- 85%+ code coverage requirement
- Happy path, error, and edge case testing
- AWS service mocking with moto
- Texas Capital header validation
- Security scenario testing

## 📝 Custom Tasks

### Code Review
Copilot is configured to provide security-focused code reviews that check:
- Texas Capital compliance
- Security vulnerabilities
- Performance considerations
- Best practice adherence

### Commit Messages
Automatic commit message generation follows conventional commit format with appropriate scopes for the loan service architecture.

### Pull Request Descriptions
Auto-generated PR descriptions include all required sections for enterprise review processes.

## 🔄 Updating Instructions

To modify Copilot behavior:

1. **Global Changes**: Edit `.github/copilot-instructions.md`
2. **Specific Tasks**: Edit relevant `.instructions.md` files
3. **New Prompts**: Add `.prompt.md` files to `.github/prompts/`
4. **VS Code Settings**: Modify `.vscode/settings.json`

## 💡 Best Practices

1. **Be Specific**: Provide context about the loan service domain when asking questions
2. **Reference Standards**: Mention "Texas Capital standards" for compliance-focused responses
3. **Use Prompts**: Leverage prompt templates for consistent results
4. **Review Generated Code**: Always review for security and business logic
5. **Update Instructions**: Keep instructions current with evolving standards

## 📚 Additional Resources

- [VS Code Copilot Documentation](https://code.visualstudio.com/docs/copilot/copilot-customization)
- [GitHub Copilot Best Practices](https://docs.github.com/en/copilot/using-github-copilot/best-practices-for-using-github-copilot)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Note**: This configuration ensures all Copilot-generated code meets enterprise standards for a production financial services application handling sensitive loan documents and customer data.
