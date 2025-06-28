# Cart Mechanism Documentation

## Overview

The cart system in this Django application provides a complete e-commerce shopping cart functionality. It handles adding products to cart, updating quantities, validating stock, and returning structured cart data.

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
- **Request Types**: Input validation schemas

### 3. **Services** (`cart/services/`)
- **CartServices**: Business logic for cart operations
- **CartHelper**: Utility functions and model conversions

### 4. **Serializers** (`cart/serializers/`)
- **CartCreateUpdateSerializer**: Handles cart item creation/updates

## Detailed Flow: Add to Cart

### Step 1: Request Input
**File**: `cart/export_types/request_data_types/add_to_cart.py`

```python
class AddToCartRequestType(BaseModel):
    user_id: Optional[str] = None
    products: Optional[List[CartProductRequestType]] = None
```

**CartProductRequestType**:
```python
class CartProductRequestType(BaseModel):
    product_id: Optional[str] = None
    quantity: Optional[int] = None
```

### Step 2: Service Layer
**File**: `cart/services/cart_services.py`

```python
@staticmethod
def add_items_to_cart(request_data: AddToCartRequestType) -> ExportCart:
    # 1. Use serializer to add items
    serializer = CartCreateUpdateSerializer()
    cart = serializer.create_or_update_cart_item(request_data)
    
    # 2. Convert to export format
    return cart_to_export(cart)
```

### Step 3: Serializer Processing
**File**: `cart/serializers/cart_serializer.py`

#### Validation Phase
```python
def validate(self, data: AddToCartRequestType):
    # 1. Validate user exists and is active
    user = User.objects.filter(id=data.user_id, is_deleted=False).first()
    if user is None:
        raise serializers.ValidationError("User not found")
    
    # 2. Validate products are in stock
    if not validate_products_in_stock_all(data.products):
        return False
    return True
```

#### Cart Item Creation/Update
```python
def create_or_update_cart_item(self, request_data: AddToCartRequestType) -> Cart | None:
    if self.validate(request_data):
        # 1. Get or create cart for user
        user = User.objects.get(id=request_data.user_id)
        cart, cart_created = Cart.objects.get_or_create(user=user)
        
        # 2. Process each product
        for product_data in requested_products:
            product = Product.objects.get(id=product_data.product_id)
            quantity = int(product_data.quantity)
            
            # 3. Get or create cart item
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart, 
                product=product,
                defaults={'quantity': quantity}
            )
            
            # 4. Update quantity if item exists
            if not item_created:
                cart_item.quantity += quantity
                cart_item.save()
        
        return cart
    return None
```

### Step 4: Stock Validation
**File**: `cart/services/cart_helper.py`

```python
def validate_products_in_stock_all(requested_products: List[CartProductRequestType]) -> bool:
    # 1. Check if product list is empty
    if not requested_products:
        raise ValidationError("Product list is empty.")
    
    # 2. Get all products from database
    product_ids = [item.product_id for item in requested_products]
    product_map = {
        str(product.id): product
        for product in Product.objects.filter(id__in=product_ids)
    }
    
    # 3. Validate each product
    for item in requested_products:
        product = product_map.get(item.product_id)
        quantity = int(item.quantity or 0)
        
        # Check product exists, is active, and has sufficient stock
        if not product:
            errors.append(f"Product with ID {item.product_id} not found.")
        elif not product.is_active:
            errors.append(f"Product '{product.name}' is inactive.")
        elif product.stock < quantity:
            errors.append(f"Product '{product.name}' has insufficient stock.")
    
    if errors:
        raise ValidationError(errors)
    
    return True
```

### Step 5: Model to Export Conversion
**File**: `cart/services/cart_helper.py`

#### Cart Item Conversion
```python
def cart_item_to_export(cart_item: CartItem) -> ExportCartItem:
    product = cart_item.product
    quantity = cart_item.quantity
    price = product.price
    
    # Calculate prices
    total_price = price * quantity
    
    # Apply discount logic (5% for 3+ items)
    line_discount = Decimal('0.00')
    if quantity >= 3:
        line_discount = total_price * Decimal('0.05')
    
    final_price = total_price - line_discount
    
    return ExportCartItem(
        id=cart_item.id,
        cart_id=cart_item.cart.id,
        product_id=product.id,
        product_name=product.name,
        product_price=price,
        product_sku=product.sku,
        product_slug=product.slug,
        category=product.category.name if product.category else None,
        brand=product.brand,
        quantity=quantity,
        stock_left=product.stock,
        is_active=product.is_active,
        is_available=product.is_active and product.stock >= quantity,
        total_price=total_price,
        line_discount=line_discount,
        final_price=final_price,
        created_at=str(cart_item.created_at),
        updated_at=str(cart_item.updated_at)
    )
```

#### Cart Conversion
```python
def cart_to_export(cart: Cart) -> ExportCart:
    # Get all cart items with related products
    cart_items = CartItem.objects.filter(cart=cart).select_related('product', 'product__category')
    
    # Convert cart items to export format
    export_items = [cart_item_to_export(item) for item in cart_items]
    
    return ExportCart(
        id=cart.id,
        user_id=cart.user.id,
        items=export_items,
        created_at=cart.created_at,
        updated_at=cart.updated_at
    )
```

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
    cart_id: Optional[uuid.UUID] = None
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
- When adding same product, quantity is accumulated

### 3. **Stock Validation**
- Validates product exists and is active
- Checks if requested quantity is available in stock
- Returns detailed error messages for validation failures

### 4. **Price Calculations**
- **Total Price**: `product_price × quantity`
- **Line Discount**: 5% discount for quantities ≥ 3
- **Final Price**: `total_price - line_discount`

### 5. **Availability Logic**
- **is_active**: Product is active in system
- **is_available**: Product is active AND has sufficient stock

## Error Handling

### Validation Errors
- User not found or inactive
- Product not found
- Product inactive
- Insufficient stock
- Empty product list

### Database Errors
- Unique constraint violations (handled by `get_or_create`)
- Foreign key violations
- Database connection issues

## Performance Optimizations

### 1. **Database Queries**
- Uses `select_related` for efficient product and category fetching
- Single query for cart items with related data
- Bulk product validation

### 2. **Memory Management**
- Lazy loading of related objects
- Efficient data conversion without unnecessary copies

## API Response Structure

### Success Response
```json
{
    "id": "uuid-string",
    "user_id": "user-uuid",
    "items": [
        {
            "id": "item-uuid",
            "cart_id": "cart-uuid",
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
```

### Error Response
```json
{
    "error": "Validation failed",
    "details": [
        "Product 'Apple iPhone' has insufficient stock: 5 available."
    ]
}
```

## Security Considerations

### 1. **User Validation**
- Validates user exists and is not deleted
- Ensures user is active before cart operations

### 2. **Data Validation**
- Input sanitization through Pydantic models
- Type checking for all input parameters
- Stock validation to prevent overselling

### 3. **Database Security**
- Uses Django ORM for SQL injection prevention
- Proper foreign key constraints
- Unique constraints to prevent data inconsistencies

## Testing Considerations

### Unit Tests
- Cart creation and retrieval
- Cart item addition and updates
- Stock validation logic
- Price calculation accuracy
- Error handling scenarios

### Integration Tests
- End-to-end cart operations
- Database constraint handling
- API response format validation
- Performance under load

## Future Enhancements

### 1. **Cart Expiration**
- Automatic cart cleanup for inactive users
- Time-based cart expiration

### 2. **Cart Merging**
- Merge guest cart with user cart on login
- Handle cart conflicts

### 3. **Advanced Discounts**
- Coupon code support
- Bulk purchase discounts
- User-specific pricing

### 4. **Cart Sharing**
- Share cart with other users
- Collaborative shopping features

This documentation provides a complete understanding of how the cart mechanism works from the initial request through to the final response, covering all components, business logic, and technical considerations. 