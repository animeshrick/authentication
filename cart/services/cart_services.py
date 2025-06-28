from auth_api.models.user_models.user import User
from cart.export_types.export_cart.export_cart import ExportCart
from cart.export_types.request_data_types.add_to_cart import AddToCartRequestType
from cart.models.cart import Cart
from cart.serializers.cart_serializer import CartCreateUpdateSerializer


class CartServices:

    @staticmethod
    def add_items_to_cart(request_data: AddToCartRequestType) -> ExportCart:
        # user = User.objects.get(id=request_data.user_id, is_deleted=False)
        # cart, _ = Cart.objects.get_or_create(user=user)
        # cart_items = []

        # for item in request_data.products:
        #     serializer = CartItemCreateUpdateSerializer(data=item)
        #     serializer.is_valid(raise_exception=True)
        #     cart_item = serializer.create_or_update_cart_item(cart)
        #     cart_items.append(cart_item)
        #
        # # Convert to ExportCartItem list
        # export_items: List[ExportCartItem] = []
        # for item in cart_items:
        #     export_items.append(ExportCartItem(
        #         id=item.id,
        #         product_id=item.product.id,
        #         product_name=item.product.name,
        #         product_price=float(item.product.price),
        #         category=item.product.category.name if item.product.category else None,
        #         brand=item.product.brand,
        #         quantity=item.quantity,
        #         stock_left=item.product.stock,
        #         is_active=item.product.is_active,
        #         is_available=item.product.is_active and item.product.stock >= item.quantity,
        #         total_price=float(item.product.price * item.quantity),
        #         line_discount=round(item.product.price * item.quantity * 0.05, 2) if item.quantity >= 3 else 0.0,
        #         final_price=round(float(item.product.price * item.quantity) - (
        #             item.product.price * item.quantity * 0.05 if item.quantity >= 3 else 0.0), 2)
        #     ))
        #
        # return ExportCart(
        #     id=cart.id,
        #     user_id=user.id,
        #     created_at=cart.created_at,
        #     items=export_items
        # )
        user_cart: ExportCart = CartCreateUpdateSerializer().create_or_update_cart_item(request_data)
        return ExportCart()