import logging
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User

logger = logging.getLogger('admin_actions')


class AdminLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log admin actions (add, update, delete)
    """
    
    def process_request(self, request):
        # Store the original request for later use
        request._admin_logging_original_path = request.path
        return None
    
    def process_response(self, request, response):
        # Only log admin actions
        if not request.path.startswith('/admin/'):
            return response
            
        # Check if user is authenticated and is staff
        if not hasattr(request, 'user') or not request.user.is_authenticated or not request.user.is_staff:
            return response
            
        # Log admin actions based on request method and path
        self._log_admin_action(request, response)
        
        return response
    
    def _log_admin_action(self, request, response):
        """Log admin actions with detailed information"""
        try:
            user = request.user
            path = request.path
            method = request.method
            
            # Determine action type based on path and method
            action = self._determine_action(path, method)
            
            if action:
                # Get object information if available
                object_info = self._get_object_info(request, path)
                
                # Log the action
                log_message = f"Admin action: {action} by user {user.username} ({user.id})"
                if object_info:
                    log_message += f" on {object_info['models']} - {object_info['object']}"
                
                logger.info(log_message, extra={
                    'user': user.username,
                    'action': action,
                    'models': object_info.get('models', 'Unknown'),
                    'object': object_info.get('object', 'Unknown'),
                    'path': path,
                    'method': method,
                    'status_code': response.status_code
                })
                
                # Also log to Django's built-in admin log if it's a models action
                if object_info and object_info.get('content_type') and object_info.get('object_id'):
                    self._log_to_django_admin_log(
                        user=user,
                        action=action,
                        content_type=object_info['content_type'],
                        object_id=object_info['object_id'],
                        object_repr=object_info['object']
                    )
                    
        except Exception as e:
            logger.error(f"Error logging admin action: {str(e)}")
    
    def _determine_action(self, path, method):
        """Determine the type of admin action based on path and method"""
        if 'add' in path and method == 'POST':
            return 'ADD'
        elif 'change' in path and method == 'POST':
            return 'CHANGE'
        elif 'delete' in path and method == 'POST':
            return 'DELETE'
        elif 'changelist' in path and method == 'POST':
            return 'BULK_ACTION'
        return None
    
    def _get_object_info(self, request, path):
        """Extract object information from the request path"""
        try:
            # Parse path like /admin/app/models/add/ or /admin/app/models/123/change/
            path_parts = path.strip('/').split('/')
            
            if len(path_parts) >= 4:
                app_label = path_parts[1]
                model_name = path_parts[2]
                
                # Try to get content type
                try:
                    content_type = ContentType.objects.get(app_label=app_label, model=model_name)
                    model = content_type.model_class()
                    
                    # Get object ID if it's a change/delete action
                    object_id = None
                    if len(path_parts) > 3 and path_parts[3].isdigit():
                        object_id = int(path_parts[3])
                        
                        # Try to get the actual object
                        try:
                            obj = model.objects.get(id=object_id)
                            object_repr = str(obj)
                        except model.DoesNotExist:
                            object_repr = f"ID: {object_id} (deleted)"
                    else:
                        object_repr = "New object"
                    
                    return {
                        'models': f"{app_label}.{model_name}",
                        'object': object_repr,
                        'content_type': content_type,
                        'object_id': object_id
                    }
                    
                except ContentType.DoesNotExist:
                    return {
                        'models': f"{app_label}.{model_name}",
                        'object': 'Unknown'
                    }
                    
        except Exception as e:
            logger.error(f"Error parsing object info: {str(e)}")
            
        return None
    
    def _log_to_django_admin_log(self, user, action, content_type, object_id, object_repr):
        """Log to Django's built-in admin log"""
        try:
            action_flag = {
                'ADD': ADDITION,
                'CHANGE': CHANGE,
                'DELETE': DELETION
            }.get(action, CHANGE)
            
            LogEntry.objects.log_action(
                user_id=user.id,
                content_type_id=content_type.id,
                object_id=object_id,
                object_repr=object_repr,
                action_flag=action_flag,
                change_message=f"Action: {action}"
            )
        except Exception as e:
            logger.error(f"Error logging to Django admin log: {str(e)}")


def log_admin_action(user, action, model_name, object_repr, object_id=None, change_message=""):
    """
    Utility function to manually log admin actions
    Usage: log_admin_action(request.user, 'ADD', 'Product', 'New Product', 123, 'Created new product')
    """
    try:
        logger.info(f"Manual admin action: {action} by {user.username} on {model_name} - {object_repr}", extra={
            'user': user.username,
            'action': action,
            'models': model_name,
            'object': object_repr,
            'object_id': object_id
        })
        
        # Also log to Django's built-in admin log
        if object_id:
            try:
                content_type = ContentType.objects.get(model=model_name.lower())
                action_flag = {
                    'ADD': ADDITION,
                    'CHANGE': CHANGE,
                    'DELETE': DELETION
                }.get(action, CHANGE)
                
                LogEntry.objects.log_action(
                    user_id=user.id,
                    content_type_id=content_type.id,
                    object_id=object_id,
                    object_repr=object_repr,
                    action_flag=action_flag,
                    change_message=change_message
                )
            except ContentType.DoesNotExist:
                pass
                
    except Exception as e:
        logger.error(f"Error in manual admin logging: {str(e)}") 