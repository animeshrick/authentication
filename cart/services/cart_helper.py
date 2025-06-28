from typing import List
from rest_framework.exceptions import ValidationError
from cart.export_types.request_data_types.cart_product import CartProductRequestType
from product.models.product import Product


def validate_products_in_stock_all(requested_products: List[CartProductRequestType]) -> bool:
    if not requested_products:
        raise ValidationError("Product list is empty.")

    product_ids = [item.product_id for item in requested_products]
    product_map = {
        str(product.id): product
        for product in Product.objects.filter(id__in=product_ids)
    }

    errors = []

    for item in requested_products:
        product = product_map.get(item.product_id)
        quantity = int(item.quantity or 0)

        if not product:
            errors.append(f"Product with ID {item.product_id} not found.")
        elif not product.is_active:
            errors.append(f"Product '{product.name}' is inactive.")
        elif product.stock < quantity:
            errors.append(
                f"Product '{product.name}' has insufficient stock: {product.stock} available."
            )

    if errors:
        raise ValidationError(errors)

    return True