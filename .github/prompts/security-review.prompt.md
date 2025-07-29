---
description: "Perform security review of API code focusing on commercial loan service requirements"
mode: "agent"
tools: ["filesystem"]
---

# Security Review for Commercial Loan API

Perform a comprehensive security review of the selected code, focusing on commercial loan service security requirements and Texas Capital standards.

## Security Review Checklist

### Input Validation
- [ ] All input parameters validated using Pydantic models
- [ ] File upload restrictions (type, size, content validation)
- [ ] SQL injection prevention
- [ ] XSS prevention in responses
- [ ] Path traversal prevention

### Authentication & Authorization
- [ ] Proper JWT token validation
- [ ] API key authentication implemented
- [ ] Role-based access control
- [ ] Session management security
- [ ] Token expiration handling

### Data Protection
- [ ] Sensitive data encryption at rest
- [ ] Sensitive data encryption in transit
- [ ] PII data handling compliance
- [ ] Financial data protection
- [ ] Audit logging for sensitive operations

### API Security
- [ ] Rate limiting implemented
- [ ] CORS properly configured
- [ ] HTTP security headers present
- [ ] Error messages don't expose sensitive info
- [ ] Proper HTTPS enforcement

### AWS Security
- [ ] IAM roles and policies properly configured
- [ ] S3 bucket permissions restricted
- [ ] DynamoDB access controls
- [ ] Secrets management (no hardcoded credentials)
- [ ] VPC security groups configured

## Output Format
Provide findings in this format:

**🔴 CRITICAL**: Issues that pose immediate security risks
**🟡 MEDIUM**: Issues that should be addressed soon
**🟢 LOW**: Best practice improvements

For each finding, include:
1. **Issue**: Clear description of the security concern
2. **Impact**: Potential consequences
3. **Recommendation**: Specific remediation steps
4. **Code Reference**: Exact file and line numbers

## Focus Areas for Commercial Loan Service
- Document upload security
- Financial data handling
- Customer PII protection
- Audit trail completeness
- Compliance with banking regulations
