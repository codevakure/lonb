---
description: "Texas Capital Standards Architecture Guidelines"
applyTo: "**/*.py"
---

# Texas Capital Standards Architecture Instructions

## Overview
This project follows a **layered architecture** that separates Texas Capital standards from business domain logic, promoting reusability, consistency, and maintainability.

## Architecture Layers

### 1. Texas Capital Standards Layer (`api/models/tc_standards.py`)
**Purpose**: Core models based on `standard-swagger-fragments.yaml`

**Contains**:
- `TCSuccessModel` - Standard success response
- `TCErrorModel` - Standard error response  
- `TCHealthCheckModel` - Standard health check response
- `TCDependencyModel` - Standard dependency model
- `TCMultiStatusModel` - Standard multi-status response
- `TCRootInfoModel` - Standard root info response
- Status enums: `HealthStatus`, `DependencyStatus`

**Rules**:
- ✅ **ONLY** models from `standard-swagger-fragments.yaml`
- ✅ **NO** business domain logic
- ✅ **NO** service-specific models
- ✅ All models must have `TC` prefix
- ✅ Must match Texas Capital standards exactly

### 2. Business Domain Layer (`api/models/business_models.py`)
**Purpose**: Domain-specific models that **extend** TC standards

**Contains**:
- `LoanProduct` - Business entity models
- `ProductListResponse` - Extends `TCSuccessModel`
- `HealthCheckResponse` - Extends `TCHealthCheckModel`
- `RootInfoResponse` - Extends `TCRootInfoModel`
- `DocumentMetadata` - Business domain models

**Rules**:
- ✅ **MUST** extend TC standard models when applicable
- ✅ **CAN** add business-specific fields
- ✅ **MUST** include schema examples in `Config.schema_extra`
- ✅ Use descriptive business names (no TC prefix)

### 3. Utility Layer (`utils/tc_standards.py`)
**Purpose**: Reusable utilities for Texas Capital standards compliance

**Contains**:
- `TCStandardHeaders` - Header management
- `TCLogger` - Standardized logging
- `TCResponse` - Response formatting

**Rules**:
- ✅ **MUST** be used in ALL endpoints
- ✅ **NO** business logic
- ✅ **ONLY** Texas Capital standard utilities

## Implementation Guidelines

### ✅ CORRECT Model Usage

```python
# TC Standards Layer - ONLY standard models
from api.models.tc_standards import TCSuccessModel, TCErrorModel, TCHealthCheckModel

# Business Layer - Extends TC standards
from api.models.business_models import LoanProduct, ProductListResponse

class ProductListResponse(TCSuccessModel):
    """Extends TC Success Model with product data"""
    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "message": "Products retrieved",
                "details": {"products": [...]}
            }
        }
```

### ❌ INCORRECT Model Usage

```python
# DON'T mix standards and business models
from api.models.tc_standards import TCSuccessModel, LoanProduct  # ❌ Wrong!

# DON'T put business models in tc_standards
class TCLoanProduct(BaseModel):  # ❌ Wrong layer!
    pass

# DON'T create non-extending business models
class CustomSuccessModel(BaseModel):  # ❌ Should extend TCSuccessModel
    pass
```

### ✅ CORRECT Endpoint Implementation

```python
from utils.tc_standards import TCStandardHeaders, TCLogger, TCResponse
from api.models.tc_standards import TCSuccessModel, TCErrorModel, TCErrorDetail
from api.models.business_models import LoanProduct

@router.get("/products", response_model=TCSuccessModel)
async def get_products(
    x_tc_request_id: Optional[str] = Header(None, alias="x-tc-request-id"),
    x_tc_correlation_id: Optional[str] = Header(None, alias="x-tc-correlation-id"),
    tc_api_key: Optional[str] = Header(None, alias="tc-api-key")
) -> TCSuccessModel:
    # ALWAYS use TC utilities
    headers = TCStandardHeaders.from_fastapi_headers(
        x_tc_request_id=x_tc_request_id,
        x_tc_correlation_id=x_tc_correlation_id,
        tc_api_key=tc_api_key
    )
    
    TCLogger.log_request("/products", headers)
    
    try:
        # Business logic
        products = [LoanProduct(...)]
        
        TCLogger.log_success("Product retrieval", headers)
        
        # ALWAYS use TC response utilities
        return TCResponse.success(
            code=200,
            message="Products retrieved successfully",
            data={"products": [p.dict() for p in products]},
            headers=headers
        )
        
    except Exception as e:
        TCLogger.log_error("Product retrieval", e, headers)
        
        error_response = TCResponse.error(
            code=500,
            message="Service error",
            headers=headers,
            error_details=[
                TCErrorDetail(source="service", message="Failed to retrieve")
            ]
        )
        
        raise HTTPException(status_code=500, detail=error_response.dict())
```

## Header Standards

### All Headers Are OPTIONAL
Based on `standard-swagger-fragments.yaml`, **ALL** Texas Capital headers are optional:

```python
# ✅ CORRECT - Headers are optional
x_tc_request_id: Optional[str] = Header(None, alias="x-tc-request-id")
x_tc_correlation_id: Optional[str] = Header(None, alias="x-tc-correlation-id") 
tc_api_key: Optional[str] = Header(None, alias="tc-api-key")

# ❌ INCORRECT - Making headers required
x_tc_request_id: str = Header(..., alias="x-tc-request-id")  # Wrong!
```

### Supported Headers
- `x-tc-request-id` - Request identifier (optional)
- `x-tc-correlation-id` - Cross-service correlation (optional)
- `tc-api-key` - API authentication (optional)
- `x-tc-integration-id` - Integration client ID (optional)
- `x-tc-utc-timestamp` - Request timestamp (optional)

## File Organization Rules

### ✅ CORRECT Structure
```
api/models/
├── tc_standards.py      # ONLY Texas Capital standard models
├── business_models.py   # Domain models extending TC standards
└── legacy_models.py     # Old models (for migration reference)

utils/
└── tc_standards.py      # TC utilities (headers, logging, responses)
```

### ❌ INCORRECT Structure
```
api/models/
├── standard_models.py   # ❌ Confusing name
├── common_models.py     # ❌ Mixes concerns
└── mixed_models.py      # ❌ Business + standards mixed
```

## Import Guidelines

### ✅ CORRECT Imports
```python
# Import TC standards first
from api.models.tc_standards import TCSuccessModel, TCErrorModel, TCErrorDetail

# Import business models second  
from api.models.business_models import LoanProduct, ProductListResponse

# Import utilities third
from utils.tc_standards import TCStandardHeaders, TCLogger, TCResponse
```

### ❌ INCORRECT Imports
```python
# Don't import everything
from api.models.tc_standards import *  # ❌ Too broad

# Don't mix layers in imports
from api.models.tc_standards import TCSuccessModel, LoanProduct  # ❌ Wrong layer

# Don't use old names
from api.models.standard_models import SuccessModel  # ❌ Deprecated
```

## Migration Guidelines

### For Existing Code
1. **Update imports** from `standard_models` → `tc_standards` + `business_models`
2. **Use TC utilities** for headers, logging, responses
3. **Make headers optional** (remove `Header(...)`, use `Header(None)`)
4. **Separate concerns** - TC standards vs business logic

### For New Code
1. **Start with TC utilities** - `TCStandardHeaders.from_fastapi_headers()`
2. **Use TC standard models** for responses - `TCSuccessModel`, `TCErrorModel`
3. **Extend for business needs** - Create business models that extend TC standards
4. **Follow naming conventions** - `TC` prefix for standards, descriptive names for business

## Testing Standards

### Model Testing
```python
def test_business_model_extends_tc_standard():
    """Ensure business models properly extend TC standards"""
    assert issubclass(ProductListResponse, TCSuccessModel)
    
def test_tc_standards_match_fragments():
    """Ensure TC models match standard-swagger-fragments.yaml"""
    model = TCSuccessModel(code=200, message="test")
    assert "code" in model.dict()
    assert "message" in model.dict()
```

### Endpoint Testing
```python
def test_endpoint_uses_tc_utilities():
    """Ensure endpoints use TC standard utilities"""
    # Test with optional headers
    response = client.get("/api/products")
    assert response.status_code == 200
    
    # Test with headers provided
    response = client.get(
        "/api/products",
        headers={
            "x-tc-request-id": "test-123",
            "x-tc-correlation-id": "corr-456"
        }
    )
    assert response.status_code == 200
```

## Validation Rules

### Before Code Review
- [ ] All endpoints use `TCStandardHeaders.from_fastapi_headers()`
- [ ] All endpoints use `TCLogger` for logging
- [ ] All endpoints use `TCResponse` for responses
- [ ] All headers are optional (`Header(None)`)
- [ ] All response models extend TC standards
- [ ] No business logic in `tc_standards.py`
- [ ] No TC standard models in `business_models.py`

### Architecture Compliance
- [ ] TC standards layer contains ONLY standard models
- [ ] Business layer extends TC standards appropriately
- [ ] Utilities layer provides reusable TC functionality
- [ ] Clear separation of concerns
- [ ] Consistent naming conventions

## Benefits of This Architecture

1. **Compliance**: Automatic Texas Capital standards compliance
2. **Consistency**: All endpoints follow same patterns
3. **Maintainability**: Clear separation of concerns
4. **Reusability**: TC utilities work across all endpoints
5. **Testability**: Easy to test standards vs business logic
6. **Scalability**: Easy to add new business models
7. **Documentation**: Self-documenting architecture
