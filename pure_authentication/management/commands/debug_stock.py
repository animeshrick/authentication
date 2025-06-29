from django.core.management.base import BaseCommand
from django.db import transaction
from product.models.product import Product
from cart.models.cart_item import CartItem
from cart.models.cart import Cart
from auth_api.models.user_models.user import User
from django.contrib.admin.models import LogEntry
from datetime import datetime, timedelta
import json


class Command(BaseCommand):
    help = 'Debug stock issues and cart operations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--product-id',
            type=str,
            help='Check stock for specific product ID'
        )
        parser.add_argument(
            '--user-id',
            type=str,
            help='Check cart for specific user ID'
        )
        parser.add_argument(
            '--fix-stock',
            action='store_true',
            help='Attempt to fix stock inconsistencies'
        )
        parser.add_argument(
            '--show-all',
            action='store_true',
            help='Show all products with stock issues'
        )
        parser.add_argument(
            '--recent-actions',
            type=int,
            default=10,
            help='Show recent admin actions (default: 10)'
        )

    def handle(self, *args, **options):
        if options['product_id']:
            self.check_product_stock(options['product_id'], options['fix_stock'])
        elif options['user_id']:
            self.check_user_cart(options['user_id'])
        elif options['show_all']:
            self.show_all_stock_issues(options['fix_stock'])
        else:
            self.show_recent_actions(options['recent_actions'])

    def check_product_stock(self, product_id, fix_stock=False):
        """Check stock for a specific product"""
        try:
            product = Product.objects.get(id=product_id)
            cart_items = CartItem.objects.filter(product=product)
            total_reserved = sum(item.quantity for item in cart_items)
            
            self.stdout.write(f"\n=== Product Stock Analysis ===")
            self.stdout.write(f"Product: {product.name} (ID: {product.id})")
            self.stdout.write(f"Current Stock: {product.stock}")
            self.stdout.write(f"Price: {product.price}")
            self.stdout.write(f"Discount: {product.discount}%")
            self.stdout.write(f"Total Reserved in Carts: {total_reserved}")
            self.stdout.write(f"Available for Purchase: {product.stock + total_reserved}")
            
            if cart_items:
                self.stdout.write(f"\nCart Reservations:")
                for item in cart_items:
                    self.stdout.write(f"  User {item.cart.user.username}: {item.quantity} units")
            
            # Check for negative stock
            if product.stock < 0:
                self.stdout.write(
                    self.style.ERROR(f"⚠️  WARNING: Product has negative stock: {product.stock}")
                )
                if fix_stock:
                    self.fix_negative_stock(product, total_reserved)
            
            # Check for excessive reservations
            if total_reserved > product.stock + total_reserved:
                self.stdout.write(
                    self.style.WARNING(f"⚠️  WARNING: More items reserved than available")
                )
                
        except Product.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Product with ID {product_id} not found")
            )

    def check_user_cart(self, user_id):
        """Check cart for a specific user"""
        try:
            user = User.objects.get(id=user_id)
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart).select_related('product')
            
            self.stdout.write(f"\n=== User Cart Analysis ===")
            self.stdout.write(f"User: {user.username} (ID: {user.id})")
            self.stdout.write(f"Cart ID: {cart.id}")
            self.stdout.write(f"Total Items: {cart_items.count()}")
            
            if cart_items:
                self.stdout.write(f"\nCart Items:")
                for item in cart_items:
                    product = item.product
                    self.stdout.write(
                        f"  {product.name}: {item.quantity} units "
                        f"(Product Stock: {product.stock})"
                    )
            else:
                self.stdout.write("  Cart is empty")
                
        except (User.DoesNotExist, Cart.DoesNotExist) as e:
            self.stdout.write(
                self.style.ERROR(f"User or cart not found: {e}")
            )

    def show_all_stock_issues(self, fix_stock=False):
        """Show all products with potential stock issues"""
        products = Product.objects.all()
        issues_found = False
        
        self.stdout.write(f"\n=== Stock Issues Analysis ===")
        
        for product in products:
            cart_items = CartItem.objects.filter(product=product)
            total_reserved = sum(item.quantity for item in cart_items)
            
            # Check for issues
            has_issue = False
            issue_type = []
            
            if product.stock < 0:
                has_issue = True
                issue_type.append("negative_stock")
            
            if total_reserved > product.stock + total_reserved:
                has_issue = True
                issue_type.append("excessive_reservations")
            
            if has_issue:
                issues_found = True
                self.stdout.write(
                    f"\n⚠️  {product.name} (ID: {product.id}):"
                )
                self.stdout.write(f"    Current Stock: {product.stock}")
                self.stdout.write(f"    Reserved: {total_reserved}")
                self.stdout.write(f"    Issues: {', '.join(issue_type)}")
                
                if fix_stock:
                    self.fix_product_stock(product, total_reserved)
        
        if not issues_found:
            self.stdout.write(
                self.style.SUCCESS("✅ No stock issues found!")
            )

    def show_recent_actions(self, limit):
        """Show recent admin actions"""
        recent_logs = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:limit]
        
        self.stdout.write(f"\n=== Recent Admin Actions (Last {limit}) ===")
        
        for log in recent_logs:
            action_map = {
                1: self.style.SUCCESS('ADD'),
                2: self.style.WARNING('CHANGE'),
                3: self.style.ERROR('DELETE'),
            }
            action = action_map.get(log.action_flag, str(log.action_flag))
            
            self.stdout.write(
                f"{log.action_time.strftime('%Y-%m-%d %H:%M:%S')} | "
                f"{action:>6} | "
                f"{log.user.username:>15} | "
                f"{log.content_type.app_label}.{log.content_type.model:>20} | "
                f"{log.object_repr[:40]}"
            )

    def fix_negative_stock(self, product, total_reserved):
        """Fix negative stock by setting it to 0"""
        try:
            with transaction.atomic():
                old_stock = product.stock
                product.stock = 0
                product.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Fixed negative stock for {product.name}: "
                        f"{old_stock} → {product.stock}"
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to fix stock: {e}")
            )

    def fix_product_stock(self, product, total_reserved):
        """Fix stock issues for a product"""
        try:
            with transaction.atomic():
                old_stock = product.stock
                
                # If stock is negative, set to 0
                if product.stock < 0:
                    product.stock = 0
                
                # If excessive reservations, adjust stock
                if total_reserved > product.stock + total_reserved:
                    product.stock = max(0, total_reserved)
                
                product.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Fixed stock for {product.name}: "
                        f"{old_stock} → {product.stock}"
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to fix stock: {e}")
            ) 