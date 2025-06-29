from typing import List
from decimal import Decimal
from rest_framework.exceptions import ValidationError
from cart.export_types.request_data_types.cart_product import CartProductRequestType
from cart.export_types.export_cart.export_cart import ExportCart
from cart.export_types.export_cart.export_cart_item import ExportCartItem
from cart.models.cart import Cart
from cart.models.cart_item import CartItem
from product.models.product import Product
from auth_api.models.user_models.user import User
from cart.models.order_summary import OrderSummary


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


def validate_stock_for_single_product(product_id: str, quantity: int, user_id: str = None) -> bool:
    """
    Validate stock for a single product
    """
    try:
        product = Product.objects.get(id=product_id)
        
        if not product.is_active:
            raise ValidationError(f"Product '{product.name}' is inactive")
        
        # Get current cart reservation if user_id provided
        current_cart_quantity = 0
        if user_id:
            try:
                user = User.objects.get(id=user_id, is_deleted=False)
                cart = Cart.objects.get(user=user)
                cart_item = CartItem.objects.filter(cart=cart, product=product).first()
                if cart_item:
                    current_cart_quantity = cart_item.quantity
            except (User.DoesNotExist, Cart.DoesNotExist):
                pass
        
        # Available stock = current stock + what's already in cart
        available_stock = product.stock + current_cart_quantity
        
        if available_stock < quantity:
            raise ValidationError(
                f"Product '{product.name}' has insufficient stock: {available_stock} available, but {quantity} requested."
            )
        
        if quantity <= 0:
            raise ValidationError(f"Product '{product.name}': Quantity must be greater than 0.")
        
        return True
        
    except Product.DoesNotExist:
        raise ValidationError(f"Product with ID {product_id} not found")


def cart_item_to_export(cart_item: CartItem) -> ExportCartItem:
    """
    Convert CartItem model to ExportCartItem using model_to_dict()
    """
    # Get cart item data using model_to_dict()
    cart_item_data = cart_item.model_to_dict()
    
    # Get product data using model_to_dict()
    product_data = cart_item.product.model_to_dict()
    
    quantity = cart_item.quantity
    price = cart_item.product.price
    discount = cart_item.product.discount or 0
    
    # Calculate prices
    total_price = price * quantity
    
    # Apply product discount (percentage)
    discount_amount = total_price * (Decimal(discount) / Decimal('100'))
    final_price = total_price - discount_amount
    
    return ExportCartItem(
        id=cart_item_data.get('id'),
        product_id=cart_item.product.id,
        product_name=product_data.get('name'),
        product_price=price,
        product_discount=discount,
        product_sku=product_data.get('sku'),
        product_slug=product_data.get('slug'),
        category=cart_item.product.category.name if cart_item.product.category else None,
        brand=product_data.get('brand'),
        quantity=quantity,
        stock_left=product_data.get('stock'),
        is_active=product_data.get('is_active'),
        is_available=product_data.get('is_active') and product_data.get('stock', 0) >= 0,
        created_at=str(cart_item_data.get('created_at')),
        updated_at=str(cart_item_data.get('updated_at'))
    )


def cart_to_export(cart: Cart) -> ExportCart:
    """
    Convert Cart model to ExportCart using model_to_dict(), and calculate OrderSummary.
    Persist OrderSummary in the database for this cart.
    """
    # Get cart data using model_to_dict()
    cart_data = cart.model_to_dict()
    
    # Get all cart items with related products
    cart_items = CartItem.objects.filter(cart=cart).select_related('product', 'product__category')
    
    # Convert cart items to export format
    export_items = [cart_item_to_export(item) for item in cart_items]
    
    # Calculate cart summary values
    total_amount = 0
    total_discount = 0
    total_items = len(export_items)
    total_quantity = len(cart_items)
    for item, cart_item in zip(export_items, cart_items):
        quantity = cart_item.quantity
        price = cart_item.product.price
        discount = cart_item.product.discount or 0
        item_total = price * quantity
        discount_amount = item_total * (Decimal(discount) / Decimal('100'))
        total_amount += item_total
        total_discount += discount_amount
    # Example: shipping charge and round off logic (customize as needed)
    shipping_charge = 0
    round_of_val = round(total_amount - total_discount) - (total_amount - total_discount)
    can_cod = 'Y'
    # Persist OrderSummary in DB (update or create for this cart)
    order_summary_obj, _ = OrderSummary.objects.update_or_create(
        id=getattr(cart, 'order_summary_id', None),
        defaults={
            'cart_amount': total_amount,
            'cart_item_discount': total_discount,
            'shipping_charge': shipping_charge,
            'round_of_val': round_of_val,
            'can_cod': can_cod,
            'total_items': total_items,
            'total_quantity': total_quantity,
            'currency': 'INR',
        }
    )
    # Optionally, link the summary to the cart if you add a OneToOneField
    # cart.order_summary = order_summary_obj
    # cart.save()
    # Prepare export dict
    order_summary = {
        'cart_amount': order_summary_obj.cart_amount,
        'cart_item_discount': order_summary_obj.cart_item_discount,
        'shipping_charge': order_summary_obj.shipping_charge,
        'round_of_val': order_summary_obj.round_of_val,
        'can_cod': order_summary_obj.can_cod,
        'total_items': order_summary_obj.total_items,
        'total_quantity': order_summary_obj.total_quantity,
        'currency': order_summary_obj.currency,
    }
    # Extract user_id from the User object (foreign key returns the object)
    user_id = cart.user.id if cart.user else None
    return ExportCart(
        id=cart_data.get('id'),
        user_id=user_id,
        items=export_items,
        order_summary=order_summary,
        created_at=cart_data.get('created_at'),
        updated_at=cart_data.get('updated_at')
    )