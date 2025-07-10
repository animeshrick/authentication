from django.shortcuts import render

def api_list_view(request):
    api_endpoints = [
        {"url": "/register", "method": "POST", "name": "Register", "description": "Register a new user"},
        {"url": "/login", "method": "POST", "name": "Login", "description": "User login"},
        {"url": "/user_details", "method": "GET", "name": "User Details", "description": "Get user details"},
        {"url": "/forgot_password", "method": "POST", "name": "Forgot Password", "description": "Reset user password"},
        {"url": "/update_password", "method": "POST", "name": "Change-User-Password", "description": "Update user password"},
        {"url": "/update_profile", "method": "POST", "name": "Update-User-profile", "description": "Update user profile"},
        {"url": "/cart/add_item", "method": "POST", "name": "Add Item to Cart", "description": "Add an item to the cart"},
        {"url": "/cart/add_to_cart", "method": "POST", "name": "Add to Cart", "description": "Add product to cart"},
        {"url": "/cart/get_cart", "method": "GET", "name": "Get Cart", "description": "Retrieve user's cart"},
        {"url": "/cart/remove_from_cart", "method": "POST", "name": "Remove from Cart", "description": "Remove item from cart"},
        {"url": "/cart/clear_cart", "method": "POST", "name": "Clear Cart", "description": "Clear all items from cart"},
        {"url": "/order/get_all_orders", "method": "GET", "name": "Get All Orders", "description": "Retrieve all orders for user"},
        {"url": "/product/get_all_products", "method": "GET", "name": "Get All Products", "description": "List all products"},
        {"url": "/product/get_product", "method": "GET", "name": "Get Product", "description": "Get product details by ID or slug"},
    ]
    return render(request, "apilist.html", {"api_endpoints": api_endpoints}) 