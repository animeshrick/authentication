# Pure Authentication API

A Django REST API for user authentication and e-commerce product management. This project provides endpoints for user registration, login, password management, profile updates, and product operations suitable for e-commerce use cases (add to cart, search, product detail page, out-of-stock indication, and order association).

## Features
- User registration and login
- Password reset and update
- User profile update and details
- Product model for e-commerce (add to cart, search, PDP, OOS, order association)
- Error handling and validation

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
   python manage.py migrate
   ```
4. **Run the development server:**
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

## Product Model
The `Product` model supports:
- Adding products to cart
- Searching products
- Displaying product detail pages (PDP)
- Showing out-of-stock (OOS) status
- Associating products with orders

Fields include: `id`, `name`, `description`, `price`, `stock`, `image`, `category`, `brand`, `is_active`, `created_at`, `updated_at`.

## License
MIT (or specify your license) 
