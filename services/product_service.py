"""
Simplified Product Service for Loan Onboarding
Following Texas Capital Standards and coretex schema
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException

from api.models.product_models import (
    SimpleProduct, 
    ProductListResponse, 
    CustomerBooking, 
    CustomersByProductResponse
)
from api.models.tc_standards import TCSuccessModel, TCErrorModel, TCErrorDetail
from config.config_kb_loan import AWS_REGION, LOAN_BOOKING_TABLE_NAME
from utils.tc_standards import TCLogger, TCStandardHeaders

logger = logging.getLogger(__name__)


class ProductService:
    """
    Simple Product Service for Loan Onboarding
    Following Texas Capital Standards
    """

    def __init__(self):
        """Initialize ProductService with simple product catalog"""
        self.service_name = "loan-onboarding-api"
        self.major_version = "v1"
        self.dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        self.bookings_table = self.dynamodb.Table(LOAN_BOOKING_TABLE_NAME)
        
        # Simple product catalog matching coretex schema - ALL 6 PRODUCTS
        self._products_catalog = [
            SimpleProduct(
                productId="equipment-financing",
                productName="Equipment Financing",
                dataSourceLocation="s3://loan-bucket/equipment-financing/"
            ),
            SimpleProduct(
                productId="term-loans",
                productName="Term Loans", 
                dataSourceLocation="s3://loan-bucket/term-loans/"
            ),
            SimpleProduct(
                productId="working-capital-loans",
                productName="Working Capital Loans",
                dataSourceLocation="s3://loan-bucket/working-capital-loans/"
            ),
            SimpleProduct(
                productId="syndicated-loans",
                productName="Syndicated Loans",
                dataSourceLocation="s3://loan-bucket/syndicated-loans/"
            ),
            SimpleProduct(
                productId="SBA-loans",
                productName="SBA Loans",
                dataSourceLocation="s3://loan-bucket/SBA-loans/"
            ),
            SimpleProduct(
                productId="LOC-loans",
                productName="LOC Loans",
                dataSourceLocation="s3://loan-bucket/LOC-loans/"
            )
        ]

    async def get_all_products(
        self,
        headers: Optional[TCStandardHeaders] = None,
        offset: int = 0,
        limit: int = 10
    ) -> TCSuccessModel:
        """
        Get all available products with pagination - TC Standard Response
        
        Args:
            headers: Texas Capital standard headers
            offset: Number of items to skip (pagination)
            limit: Number of items to return (pagination)
            
        Returns:
            TCSuccessModel: Standard TC response with paginated product data
        """
        try:
            TCLogger.log_info(
                "Retrieving loan products", 
                headers, 
                {"total_products": len(self._products_catalog), "offset": offset, "limit": limit}
            )

            # Apply pagination to products catalog
            total_products = len(self._products_catalog)
            paginated_products = self._products_catalog[offset:offset + limit]
            
            # Convert products to dict format for TC response
            products_data = [product.model_dump() for product in paginated_products]

            response = TCSuccessModel(
                code=200,
                message="Products retrieved successfully",
                details={
                    "products": products_data,
                    "total": total_products,
                    "offset": offset,
                    "limit": limit,
                    "returned": len(products_data),
                    "service": "ProductService",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            TCLogger.log_success(
                "Products retrieved successfully", 
                headers, 
                {"total_products": total_products, "returned": len(products_data), "offset": offset, "limit": limit}
            )
            
            return response
            
        except Exception as e:
            TCLogger.log_error(
                "Product retrieval failed", 
                e, 
                headers,
                {"service": "ProductService.get_all_products"}
            )
            
            # Return TC standard error response
            error_response = TCErrorModel(
                code=500,
                serviceName=self.service_name,
                majorVersion=self.major_version,
                timestamp=datetime.now().isoformat(),
                message="Product retrieval failed",
                details=[
                    TCErrorDetail(
                        source="ProductService.get_all_products",
                        message=str(e)
                    )
                ]
            )
            raise HTTPException(status_code=500, detail=error_response.model_dump())

    async def get_customers_by_product(
        self, 
        product_name: str,
        headers: Optional[TCStandardHeaders] = None,
        offset: int = 0,
        limit: int = 10
    ) -> TCSuccessModel:
        """
        Get customers filtered by product name with pagination - TC Standard Response
        
        Args:
            product_name: Product name to filter by
            headers: Texas Capital standard headers
            offset: Number of items to skip (pagination)
            limit: Number of items to return (pagination)
            
        Returns:
            TCSuccessModel: Standard TC response with paginated customer data
        """
        try:
            TCLogger.log_info(
                "Retrieving customers by product", 
                headers, 
                {"product_name": product_name, "offset": offset, "limit": limit}
            )

            # Query DynamoDB for bookings
            try:
                response = self.bookings_table.scan(
                    FilterExpression='productName = :p',
                    ExpressionAttributeValues={':p': product_name}
                )
                booking_items = response.get('Items', [])
                
            except ClientError as e:
                logger.error(f"DynamoDB scan failed: {e}")
                booking_items = []

            # Convert DynamoDB items to CustomerBooking models
            customers = []
            for item in booking_items:
                try:
                    customer = CustomerBooking(
                        loan_booking_id=item.get('loanBookingId', ''),
                        customer_name=item.get('customerName', ''),
                        product_name=item.get('productName', ''),
                        data_source_location=item.get('dataSourceLocation', ''),
                        document_ids=item.get('documentIds', []),
                        booking_status=item.get('status', 'pending'),
                        created_timestamp=item.get('timestamp'),
                        metadata=item.get('metadata', {})
                    )
                    customers.append(customer)
                except Exception as e:
                    logger.warning(f"Failed to parse booking item: {e}")
                    continue

            # Apply pagination to customers
            total_customers = len(customers)
            paginated_customers = customers[offset:offset + limit]
            
            # Generate summary
            summary = self._generate_customer_summary(customers)  # Summary based on all customers
            
            # Convert paginated customers to dict format
            customers_data = [customer.model_dump() for customer in paginated_customers]

            response = TCSuccessModel(
                code=200,
                message="Customers retrieved successfully",
                details={
                    "product_name": product_name,
                    "customers": customers_data,
                    "total_customers": total_customers,
                    "offset": offset,
                    "limit": limit,
                    "returned": len(customers_data),
                    "summary": summary,
                    "service": "ProductService",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            TCLogger.log_success(
                "Customers retrieved successfully", 
                headers, 
                {"product_name": product_name, "total_customers": total_customers, "returned": len(customers_data), "offset": offset, "limit": limit}
            )
            
            return response
            
        except Exception as e:
            TCLogger.log_error(
                "Customer retrieval by product failed", 
                e, 
                headers,
                {"product_name": product_name}
            )
            
            # Return TC standard error response
            error_response = TCErrorModel(
                code=500,
                serviceName=self.service_name,
                majorVersion=self.major_version,
                timestamp=datetime.now().isoformat(),
                message="Customer retrieval failed",
                details=[
                    TCErrorDetail(
                        source="ProductService.get_customers_by_product",
                        message=str(e)
                    )
                ]
            )
            raise HTTPException(status_code=500, detail=error_response.model_dump())

    def _generate_customer_summary(self, customers: List[CustomerBooking]) -> Dict[str, Any]:
        """Generate summary statistics for customer bookings"""
        status_counts = {}
        document_count = 0
        
        for customer in customers:
            # Count by status
            status = customer.booking_status
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count documents
            document_count += len(customer.document_ids)
        
        return {
            "total_customers": len(customers),
            "status_breakdown": status_counts,
            "total_document_count": document_count,
            "average_documents_per_customer": round(document_count / len(customers), 2) if customers else 0
        }

    def get_product_s3_prefix(self, product_id: str) -> Optional[str]:
        """Get S3 folder prefix for a product"""
        for product in self._products_catalog:
            if product.productId == product_id:
                return product.dataSourceLocation
        return None
