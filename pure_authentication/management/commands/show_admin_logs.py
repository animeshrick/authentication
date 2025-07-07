from django.core.management.base import BaseCommand
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta
import argparse


class Command(BaseCommand):
    help = 'Display admin action logs with filtering options'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action-type',
            choices=['add', 'change', 'delete'],
            help='Filter by action type (add, change, delete)'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Filter by username'
        )
        parser.add_argument(
            '--models',
            type=str,
            help='Filter by models name'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Show logs from last N days (default: 7)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Limit number of results (default: 50)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information'
        )

    def handle(self, *args, **options):
        # Build queryset
        logs = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')
        
        # Apply filters
        if options['days']:
            date_from = datetime.now() - timedelta(days=options['days'])
            logs = logs.filter(action_time__gte=date_from)
        
        if options['action_type']:
            action_map = {
                'add': 1,
                'change': 2,
                'delete': 3,
            }
            logs = logs.filter(action_flag=action_map[options['action_type']])
        
        if options['user']:
            logs = logs.filter(user__username__icontains=options['user'])
        
        if options['models']:
            logs = logs.filter(content_type__model__icontains=options['models'])
        
        # Apply limit
        logs = logs[:options['limit']]
        
        # Display results
        if not logs:
            self.stdout.write(
                self.style.WARNING('No admin logs found matching the criteria.')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Found {len(logs)} admin log entries:')
        )
        self.stdout.write('=' * 80)
        
        for log in logs:
            # Format action type
            action_map = {
                1: self.style.SUCCESS('ADD'),
                2: self.style.WARNING('CHANGE'),
                3: self.style.ERROR('DELETE'),
            }
            action = action_map.get(log.action_flag, str(log.action_flag))
            
            # Basic info
            self.stdout.write(
                f"{log.action_time.strftime('%Y-%m-%d %H:%M:%S')} | "
                f"{action:>6} | "
                f"{log.user.username:>15} | "
                f"{log.content_type.app_label}.{log.content_type.model:>20} | "
                f"{log.object_repr[:40]}"
            )
            
            # Verbose output
            if options['verbose']:
                self.stdout.write(f"    Object ID: {log.object_id}")
                self.stdout.write(f"    Change Message: {log.change_message}")
                self.stdout.write('-' * 80)
        
        # Show summary
        self.stdout.write('=' * 80)
        self.stdout.write(
            self.style.SUCCESS(f'Total: {len(logs)} entries')
        )
        
        # Show action type breakdown
        action_counts = {}
        for log in logs:
            action_type = log.action_flag
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        if action_counts:
            self.stdout.write('\nAction breakdown:')
            for action_type, count in action_counts.items():
                action_name = {1: 'Add', 2: 'Change', 3: 'Delete'}.get(action_type, f'Type {action_type}')
                self.stdout.write(f"  {action_name}: {count}") 