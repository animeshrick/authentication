# Pure Authentication API

A Django REST API for user authentication and e-commerce product management. This project provides endpoints for user registration, login, password management, profile updates, and product operations suitable for e-commerce use cases (search, product detail page, out-of-stock indication, and order association).

## Features
- User registration and login
- Password reset and update
- User profile update and details
- Product model for e-commerce (search, PDP, OOS, order association)
- Category model with slug auto-generation
- Product SKU and slug auto-generation
- Product-Category mapping (each product belongs to a category)
- Products can only be added if stock > 0
- Error handling and validation
- ProductService for SKU and product name uniqueness checks

## Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd pure_authentication
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Apply migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. **Create a superuser (optional, for admin):**
   ```bash
   python manage.py createsuperuser
   ```
5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

| URL                | Method | Name                  | Description                        |
|--------------------|--------|-----------------------|------------------------------------|
| `/register`        | POST   | Register              | Register a new user                |
| `/login`           | POST   | Login                 | User login                         |
| `/user_details`    | GET    | User Details          | Get user details                   |
| `/forgot_password` | POST   | Forgot Password       | Reset user password                |
| `/update_password` | POST   | Change-User-Password  | Update user password               |
| `/update_profile`  | POST   | Update-User-profile   | Update user profile                |

> **Note:** All endpoints expect and return JSON. Refer to the code for required request fields.

## Product & Category Models

### Product
- Fields: `name`, `slug` (auto), `sku` (auto), `description`, `price`, `stock`, `image`, `category` (FK), `brand`, `is_active`, etc.
- **SKU**: Auto-generated if not provided, unique for each product.
- **Slug**: Auto-generated from name, unique for each product.
- **Category**: ForeignKey to Category; each product belongs to a category.
- **Stock Constraint**: Products can only be added if `stock > 0` (enforced at model level).

### Category
- Fields: `name`, `slug` (auto), etc.
- **Slug**: Auto-generated from name, unique for each category.

### ProductService
- Use `ProductService.is_unique_sku(sku)` to check SKU uniqueness.
- Use `ProductService.is_unique_product_name_in_category(name, category)` to check product name uniqueness within a category.

## How to Use

### Admin Panel
- Visit `/admin/` to add/manage products and categories.
- Only products with `stock > 0` can be added.
- Slugs and SKUs are auto-generated if not provided.

### API Usage
- Use the endpoints above to register, login, and manage user profiles.
- Extend with product/category endpoints as needed for your frontend.

** Live URL: https://authentication-01s3.onrender.com **

## License
MIT (or specify your license) 
