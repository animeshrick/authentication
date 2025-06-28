from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('admin_actions')


@staff_member_required
def admin_log_view(request):
    """
    Custom admin view to display admin logs with filtering options
    """
    # Get filter parameters
    action_type = request.GET.get('action_type', '')
    user_id = request.GET.get('user_id', '')
    model_name = request.GET.get('model_name', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    logs = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')
    
    # Apply filters
    if action_type:
        action_map = {
            'add': 1,  # ADDITION
            'change': 2,  # CHANGE
            'delete': 3,  # DELETION
        }
        if action_type in action_map:
            logs = logs.filter(action_flag=action_map[action_type])
    
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    if model_name:
        logs = logs.filter(content_type__model__icontains=model_name)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            logs = logs.filter(action_time__date__gte=date_from_obj.date())
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            logs = logs.filter(action_time__date__lte=date_to_obj.date())
        except ValueError:
            pass
    
    # Pagination
    paginator = Paginator(logs, 50)  # 50 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    users = User.objects.filter(is_staff=True).order_by('username')
    content_types = ContentType.objects.filter(
        id__in=logs.values_list('content_type', flat=True).distinct()
    ).order_by('app_label', 'model')
    
    context = {
        'page_obj': page_obj,
        'users': users,
        'content_types': content_types,
        'action_types': [
            ('add', 'Add'),
            ('change', 'Change'),
            ('delete', 'Delete'),
        ],
        'filters': {
            'action_type': action_type,
            'user_id': user_id,
            'model_name': model_name,
            'date_from': date_from,
            'date_to': date_to,
        }
    }
    
    return render(request, 'admin/admin_logs.html', context)


@staff_member_required
def admin_dashboard_view(request):
    """
    Admin dashboard showing recent admin actions and statistics
    """
    # Get recent admin actions (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_logs = LogEntry.objects.filter(
        action_time__gte=seven_days_ago
    ).select_related('user', 'content_type').order_by('-action_time')[:20]
    
    # Get statistics
    total_actions = LogEntry.objects.count()
    today_actions = LogEntry.objects.filter(
        action_time__date=datetime.now().date()
    ).count()
    
    # Actions by type
    add_actions = LogEntry.objects.filter(action_flag=1).count()
    change_actions = LogEntry.objects.filter(action_flag=2).count()
    delete_actions = LogEntry.objects.filter(action_flag=3).count()
    
    # Top active users
    top_users = LogEntry.objects.values('user__username').annotate(
        action_count=Count('id')
    ).order_by('-action_count')[:10]
    
    # Top modified models
    top_models = LogEntry.objects.values('content_type__app_label', 'content_type__model').annotate(
        action_count=Count('id')
    ).order_by('-action_count')[:10]
    
    context = {
        'recent_logs': recent_logs,
        'total_actions': total_actions,
        'today_actions': today_actions,
        'add_actions': add_actions,
        'change_actions': change_actions,
        'delete_actions': delete_actions,
        'top_users': top_users,
        'top_models': top_models,
    }
    
    return render(request, 'admin/admin_dashboard.html', context)


class AdminLogListView(ListView):
    """
    Class-based view for admin logs with advanced filtering
    """
    model = LogEntry
    template_name = 'admin/admin_log_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')
        
        # Apply filters from query parameters
        filters = {}
        
        if self.request.GET.get('action_type'):
            action_map = {
                'add': 1,
                'change': 2,
                'delete': 3,
            }
            action_type = self.request.GET.get('action_type')
            if action_type in action_map:
                filters['action_flag'] = action_map[action_type]
        
        if self.request.GET.get('user_id'):
            filters['user_id'] = self.request.GET.get('user_id')
        
        if self.request.GET.get('model_name'):
            filters['content_type__model__icontains'] = self.request.GET.get('model_name')
        
        if self.request.GET.get('date_from'):
            try:
                date_from = datetime.strptime(self.request.GET.get('date_from'), '%Y-%m-%d')
                filters['action_time__date__gte'] = date_from.date()
            except ValueError:
                pass
        
        if self.request.GET.get('date_to'):
            try:
                date_to = datetime.strptime(self.request.GET.get('date_to'), '%Y-%m-%d')
                filters['action_time__date__lte'] = date_to.date()
            except ValueError:
                pass
        
        return queryset.filter(**filters)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options
        context['users'] = User.objects.filter(is_staff=True).order_by('username')
        context['content_types'] = ContentType.objects.all().order_by('app_label', 'model')
        context['action_types'] = [
            ('add', 'Add'),
            ('change', 'Change'),
            ('delete', 'Delete'),
        ]
        
        # Add current filters
        context['filters'] = {
            'action_type': self.request.GET.get('action_type', ''),
            'user_id': self.request.GET.get('user_id', ''),
            'model_name': self.request.GET.get('model_name', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
        }
        
        return context


# Import Count for the dashboard view
from django.db.models import Count 