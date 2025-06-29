# Cart Mechanism Documentation

## Overview

The cart system in this Django application provides a complete e-commerce shopping cart functionality with robust stock management, transaction safety, and comprehensive validation. It handles adding products to cart, updating quantities, validating stock, removing items, clearing carts, and returning structured cart data.

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

## Detailed Flow: Add to Cart

### Step 1: Request Input
The API accepts a POST request with user_id and products list:

```json
{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "products": [
        {
            "product_id": "987fcdeb-51a2-43d1-b789-123456789abc",
            "quantity": 2
        }
    ]
}
```

### Step 2: Service Layer
**File**: `cart/services/cart_services.py`

```python
@staticmethod
def add_items_to_cart(request_data: AddToCartRequestType) -> ExportCart:
    try:
        serializer = CartCreateUpdateSerializer()
        
        # Use the improved stock validation method
        if not serializer.validate_stock_with_transaction(request_data):
            raise ValueError("Stock validation failed")
        
        cart = serializer.create_or_update_cart_item(request_data)
        
        if cart is None:
            raise ValueError("Failed to add items to cart")
        
        return cart_to_export(cart)
        
    except Exception as e:
        raise
```

### Step 3: Enhanced Serializer Processing
**File**: `cart/serializers/cart_serializer.py`

#### Transaction-Safe Stock Validation
```python
def validate_stock_with_transaction(self, request_data: AddToCartRequestType) -> bool:
    try:
        with transaction.atomic():
            user = User.objects.get(id=request_data.user_id, is_deleted=False)
            cart, _ = Cart.objects.get_or_create(user=user)
            
            requested_products = request_data.products or []
            product_ids = [p.product_id for p in requested_products]
            
            # Get products with select_for_update to lock them
            products = Product.objects.select_for_update().filter(id__in=product_ids)
            product_map = {p.id: p for p in products}
            
            # Get current cart items
            cart_items = CartItem.objects.select_for_update().filter(cart=cart, product_id__in=product_ids)
            cart_reservations = {item.product_id: item.quantity for item in cart_items}
            
            # Validate stock for each product
            for product_data in requested_products:
                product = product_map.get(product_data.product_id)
                quantity = int(product_data.quantity or 0)
                
                if not product:
                    raise serializers.ValidationError(f"Product with ID {product_data.product_id} not found")
                
                if not product.is_active:
                    raise serializers.ValidationError(f"Product '{product.name}' is inactive")
                
                # Get current cart reservation for this product
                current_cart_quantity = cart_reservations.get(product_data.product_id, 0)
                
                # Calculate available stock (current stock + what's already in cart)
                available_stock = product.stock + current_cart_quantity
                
                if available_stock < quantity:
                    raise serializers.ValidationError(
                        f"Product '{product.name}' has insufficient stock: {available_stock} available, but {quantity} requested."
                    )
                
                if quantity <= 0:
                    raise serializers.ValidationError(f"Product '{product.name}': Quantity must be greater than 0.")
            
            return True
            
    except Exception as e:
        return False
```

#### Atomic Cart Item Creation/Update
```python
@transaction.atomic
def create_or_update_cart_item(self, request_data: AddToCartRequestType) -> Cart | None:
    if not self.validate(request_data):
        return None
        
    try:
        user = User.objects.get(id=request_data.user_id)
        cart, cart_created = Cart.objects.get_or_create(user=user)

        requested_products: List[CartProductRequestType] = request_data.products or []
        product_ids = [p.product_id for p in requested_products]
        
        # Bulk fetch products and cart items with select_for_update to prevent race conditions
        products = Product.objects.select_for_update().filter(id__in=product_ids)
        product_map = {p.id: p for p in products}
        cart_items = CartItem.objects.select_for_update().filter(cart=cart, product_id__in=product_ids)
        cart_item_map = {item.product_id: item for item in cart_items}

        # Prepare bulk operations
        products_to_update = []
        cart_items_to_update = []
        cart_items_to_create = []

        for product_data in requested_products:
            product = product_map.get(product_data.product_id)
            quantity = int(product_data.quantity)
            
            if not product:
                continue
                
            cart_item = cart_item_map.get(product.id)
            
            if cart_item:
                # Update existing cart item
                old_quantity = cart_item.quantity
                new_quantity = quantity
                stock_adjustment = new_quantity - old_quantity
                
                if stock_adjustment != 0:
                    # Use F() expression to prevent race conditions
                    product.stock = F('stock') - stock_adjustment
                    products_to_update.append(product)
                
                cart_item.quantity = new_quantity
                cart_items_to_update.append(cart_item)
            else:
                # Create new cart item
                cart_item = CartItem(cart=cart, product=product, quantity=quantity)
                cart_items_to_create.append(cart_item)
                
                # Use F() expression to prevent race conditions
                product.stock = F('stock') - quantity
                products_to_update.append(product)

        # Execute bulk operations
        if products_to_update:
            Product.objects.bulk_update(products_to_update, ["stock"])
            
        if cart_items_to_update:
            CartItem.objects.bulk_update(cart_items_to_update, ["quantity"])
            
        if cart_items_to_create:
            CartItem.objects.bulk_create(cart_items_to_create)

        return cart
        
    except Exception as e:
        # Transaction will be rolled back automatically
        raise
```

### Step 4: Enhanced Stock Validation
**File**: `cart/services/cart_helper.py`

```python
def validate_products_in_stock_all(requested_products: List[CartProductRequestType], user_id: str = None) -> bool:
    """
    Validate that all requested products have sufficient stock
    This function is used for initial validation before transaction
    """
    if not requested_products:
        raise ValidationError("Product list is empty.")

    product_ids = [item.product_id for item in requested_products]
    
    # Get all products in a single query
    products = Product.objects.filter(id__in=product_ids)
    product_map = {product.id: product for product in products}

    # Get current cart items for the user (if user_id provided)
    cart_reservations = {}
    if user_id:
        try:
            user = User.objects.get(id=user_id, is_deleted=False)
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart, product_id__in=product_ids)
            cart_reservations = {item.product_id: item.quantity for item in cart_items}
        except (User.DoesNotExist, Cart.DoesNotExist):
            pass

    errors = []

    for item in requested_products:
        product = product_map.get(item.product_id)
        quantity = int(item.quantity or 0)
        
        # Get current cart reservation for this product
        current_cart_quantity = cart_reservations.get(item.product_id, 0)
        
        # Available stock = current stock + what's already in cart (since we'll be updating the cart)
        available_stock = product.stock + current_cart_quantity if product else 0

        if not product:
            errors.append(f"Product with ID {item.product_id} not found in database.")
        elif not product.is_active:
            errors.append(f"Product '{product.name}' is inactive and cannot be added to cart.")
        elif available_stock < quantity:
            errors.append(
                f"Product '{product.name}' has insufficient stock: {available_stock} available (including current cart), but {quantity} requested."
            )
        elif quantity <= 0:
            errors.append(f"Product '{product.name}': Quantity must be greater than 0.")

    if errors:
        raise ValidationError(errors)

    return True
```

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