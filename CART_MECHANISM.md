# Cart Mechanism Documentation

## Overview

The cart system in this Django application provides robust e-commerce shopping cart functionality with strong stock management, transaction safety, and comprehensive validation. It handles adding products to cart, updating quantities, validating stock, removing items, clearing carts, and returning structured cart data.

## Architecture Flow

```
View → Service → Serializer → Model → Export Type → Response
```

## Components Overview

### 1. **Models** (`cart/models/`)
- **Cart**: Represents a user's shopping cart
- **CartItem**: Individual items within a cart

### 2. **Export Types** (`cart/export_types/`)
- **ExportCart**: Structured cart data for API responses
- **ExportCartItem**: Structured cart item data
- **Request Types**: Input validation schemas for all operations

### 3. **Services** (`cart/services/`)
- **CartServices**: Business logic for cart operations with transaction safety
- **CartHelper**: Utility functions and model conversions

### 4. **Serializers** (`cart/serializers/`)
- **CartCreateUpdateSerializer**: Handles cart item creation/updates with atomic operations

### 5. **Views** (`cart/views/`)
- **AddToCartView**: Add items to cart
- **GetCartView**: Retrieve cart contents
- **RemoveFromCartView**: Remove specific items
- **ClearCartView**: Clear entire cart

## Request Data Types

### Add to Cart Request
**File**: `cart/export_types/request_data_types/add_to_cart.py`

```python
class AddToCartRequestType(BaseModel):
    user_id: Optional[uuid.UUID] = None
    products: Optional[List[CartProductRequestType]] = None
```

### Cart Product Request
**File**: `cart/export_types/request_data_types/cart_product.py`

```python
class CartProductRequestType(BaseModel):
    product_id: Optional[uuid.UUID] = None
    quantity: Optional[int] = None
```

### Remove from Cart Request
**File**: `cart/export_types/request_data_types/remove_from_cart.py`

```python
class RemoveFromCartRequestType(BaseModel):
    user_id: uuid.UUID = Field(..., description="User ID")
    product_id: uuid.UUID = Field(..., description="Product ID to remove from cart")
```

### Get Cart Request
**File**: `cart/export_types/request_data_types/get_cart.py`

```python
class GetCartRequestType(BaseModel):
    user_id: uuid.UUID = Field(..., description="User ID to get cart for")
```

## Add to Cart Flow (Atomic & Validated)

1. **Request Input:**
   - API accepts a POST request with `user_id` and a list of products (each with `product_id` and `quantity`).
2. **Service Layer:**
   - `CartServices.add_items_to_cart` uses `CartCreateUpdateSerializer` for validation and atomic operations.
   - Stock is validated with a transaction to prevent race conditions.
3. **Serializer:**
   - Validates product existence, activeness, and available stock (including current cart reservations).
   - Ensures no more items are added than available.
   - Handles both creation and update of cart items atomically.
4. **Model & Export:**
   - Cart and CartItem models are updated.
   - Export types are used to return structured cart and item data in API responses.

## Key Points
- All cart operations are atomic and transaction-safe.
- Stock validation prevents overselling and race conditions.
- Cart is always up to date with product stock and user actions.
- API returns clear error messages for invalid operations (inactive product, insufficient stock, etc).

Refer to the codebase for detailed implementation in `cart/services/`, `cart/serializers/`, and `cart/views/`.

## Cart Operations

### 1. **Add to Cart**
- **Endpoint**: `POST /cart/add_to_cart`
- **Features**: 
  - Transaction-safe stock validation
  - Atomic cart item creation/updates
  - Race condition prevention
  - Bulk operations for performance

### 2. **Get Cart**
- **Endpoint**: `GET /cart/get_cart?user_id=<uuid>` or `POST /cart/get_cart`
- **Features**:
  - Flexible parameter handling (query params or request body)
  - Returns empty cart if none exists
  - Includes all cart items with product details

### 3. **Remove from Cart**
- **Endpoint**: `POST /cart/remove_from_cart`
- **Features**:
  - Transaction-safe stock restoration
  - Proper validation with Pydantic models
  - Automatic stock adjustment

### 4. **Clear Cart**
- **Endpoint**: `POST /cart/clear_cart`
- **Features**:
  - Transaction-safe bulk stock restoration
  - Removes all items from cart
  - Restores stock for all products

## Data Models

### Cart Model
```python
class Cart(GenericBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts', db_index=True)
```

**Fields**:
- `id`: UUID (from GenericBaseModel)
- `user`: ForeignKey to User
- `created_at`: DateTime (from GenericBaseModel)
- `updated_at`: DateTime (from GenericBaseModel)

### CartItem Model
```python
class CartItem(GenericBaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('cart', 'product')
```

**Fields**:
- `id`: UUID (from GenericBaseModel)
- `cart`: ForeignKey to Cart
- `product`: ForeignKey to Product
- `quantity`: PositiveIntegerField
- `created_at`: DateTime (from GenericBaseModel)
- `updated_at`: DateTime (from GenericBaseModel)

## Export Types

### ExportCart
```python
class ExportCart(BaseModel):
    id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    items: List[ExportCartItem] = []
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
```

### ExportCartItem
```python
class ExportCartItem(BaseModel):
    id: Optional[uuid.UUID] = None
    product_id: Optional[uuid.UUID] = None
    product_name: Optional[str] = None
    product_price: Optional[Decimal] = None
    product_sku: Optional[str] = None
    product_slug: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    quantity: int = 1
    stock_left: int = 0
    is_active: bool = True
    is_available: bool = True
    total_price: Optional[Decimal] = None
    line_discount: Optional[Decimal] = None
    final_price: Optional[Decimal] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
```

## Business Logic

### 1. **Cart Creation**
- Each user can have only one cart
- Cart is created automatically when first item is added
- Uses `get_or_create` to prevent duplicates

### 2. **Cart Item Management**
- Same product cannot be added twice to the same cart
- Uses `unique_together` constraint on (cart, product)
- When adding same product, quantity is updated (not accumulated)

### 3. **Stock Management**
- **Reservation System**: Stock is reduced when items are added to cart
- **Restoration System**: Stock is restored when items are removed from cart
- **Validation**: Checks available stock including current cart reservations
- **Atomic Operations**: All stock changes are transaction-safe

### 4. **Price Calculations**
- **Total Price**: `product_price × quantity`
- **Line Discount**: 5% discount for quantities ≥ 3
- **Final Price**: `total_price - line_discount`

### 5. **Availability Logic**
- **is_active**: Product is active in system
- **is_available**: Product is active AND has sufficient stock

## Transaction Safety & Race Condition Prevention

### 1. **Database Transactions**
- All cart operations are wrapped in `@transaction.atomic`
- Automatic rollback on errors
- Consistent data state

### 2. **Row-Level Locking**
- Uses `select_for_update()` to lock records during operations
- Prevents concurrent modifications to same products
- Ensures stock accuracy

### 3. **Atomic Updates**
- Uses Django's `F()` expressions for stock updates
- Prevents race conditions in stock calculations
- Database-level atomicity

### 4. **Bulk Operations**
- Efficient bulk updates for multiple products
- Reduced database round trips
- Better performance for large cart operations

## Error Handling

### Validation Errors
- User not found or inactive
- Product not found or inactive
- Insufficient stock
- Invalid quantities
- Empty product list

### Transaction Errors
- Database constraint violations
- Deadlock detection and handling
- Automatic rollback on failures

### API Errors
- Proper HTTP status codes
- Structured error responses
- Clear error messages

## Performance Optimizations

### 1. **Database Queries**
- Uses `select_related` for efficient product and category fetching
- Single query for cart items with related data
- Bulk product validation
- Optimized bulk operations

### 2. **Memory Management**
- Lazy loading of related objects
- Efficient data conversion without unnecessary copies
- Minimal memory footprint

### 3. **Concurrency Handling**
- Row-level locking prevents conflicts
- Atomic operations ensure consistency
- Efficient handling of concurrent requests

## API Response Structure

### Success Response
```json
{
    "message": "Products added to cart successfully.",
    "data": {
        "id": "uuid-string",
        "user_id": "user-uuid",
        "items": [
            {
                "id": "item-uuid",
                "product_id": "product-uuid",
                "product_name": "Product Name",
                "product_price": "99.99",
                "product_sku": "SKU123",
                "product_slug": "product-name",
                "category": "Category Name",
                "brand": "Brand Name",
                "quantity": 2,
                "stock_left": 50,
                "is_active": true,
                "is_available": true,
                "total_price": "199.98",
                "line_discount": "9.99",
                "final_price": "189.99",
                "created_at": "2024-01-01T10:00:00Z",
                "updated_at": "2024-01-01T10:00:00Z"
            }
        ],
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
    }
}
```

### Error Response
```json
{
    "message": "Validation failed",
    "details": [
        "Product 'Apple iPhone' has insufficient stock: 5 available, but 10 requested."
    ]
}
```

## Security Considerations

### 1. **User Validation**
- Validates user exists and is not deleted
- Ensures user is active before cart operations
- UUID validation for user IDs

### 2. **Data Validation**
- Input sanitization through Pydantic models
- Type checking for all input parameters
- Stock validation to prevent overselling
- Quantity validation (must be positive)

### 3. **Database Security**
- Uses Django ORM for SQL injection prevention
- Proper foreign key constraints
- Unique constraints to prevent data inconsistencies
- Transaction safety prevents partial updates

## Debugging & Monitoring

### 1. **Management Commands**
- `python manage.py debug_stock --product-id <uuid>`: Check specific product stock
- `python manage.py debug_stock --user-id <uuid>`: Check user cart
- `python manage.py debug_stock --show-all`: Find all stock issues
- `python manage.py debug_stock --show-all --fix-stock`: Fix stock issues
- `python manage.py show_admin_logs`: View admin action logs

### 2. **Stock Debugging**
- Comprehensive stock analysis
- Cart reservation tracking
- Stock inconsistency detection
- Automatic stock fixing capabilities

## Testing Considerations

### Unit Tests
- Cart creation and retrieval
- Cart item addition and updates
- Stock validation logic
- Price calculation accuracy
- Error handling scenarios
- Transaction rollback testing

### Integration Tests
- End-to-end cart operations
- Database constraint handling
- API response format validation
- Performance under load
- Concurrent request handling

### Load Testing
- Multiple concurrent cart operations
- Stock reservation accuracy under load
- Transaction performance
- Database connection handling

## Future Enhancements

### 1. **Cart Expiration**
- Automatic cart cleanup for inactive users
- Time-based cart expiration
- Stock restoration on expiration

### 2. **Cart Merging**
- Merge guest cart with user cart on login
- Handle cart conflicts
- Preserve cart history

### 3. **Advanced Discounts**
- Coupon code support
- Bulk purchase discounts
- User-specific pricing
- Dynamic discount rules

### 4. **Cart Sharing**
- Share cart with other users
- Collaborative shopping features
- Cart templates

### 5. **Stock Alerts**
- Low stock notifications
- Back-in-stock alerts
- Stock reservation timeouts

### 6. **Analytics**
- Cart abandonment tracking
- Popular product combinations
- Stock movement analytics
- User behavior insights

This documentation provides a complete understanding of the enhanced cart mechanism with transaction safety, race condition prevention, and robust stock management from the initial request through to the final response, covering all components, business logic, and technical considerations. 