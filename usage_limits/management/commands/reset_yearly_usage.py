# usage_limits/management/commands/reset_yearly_usage.py - Enhanced with better reliability

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import stripe
from django.conf import settings

from subscriptions.models import CustomerSubscription
from usage_limits.usage_tracker import UsageTracker

User = get_user_model()

class Command(BaseCommand):
    help = 'Enhanced yearly usage reset with better reliability and monitoring'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Reset specific user ID',
        )
        parser.add_argument(
            '--username', 
            type=str,
            help='Reset specific username',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be reset without actually resetting',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reset even if not due',
        )
        parser.add_argument(
            '--show-eligible',
            action='store_true',
            help='Show all users eligible for reset',
        )
        parser.add_argument(
            '--auto-reset',
            action='store_true',
            help='Automatically reset all eligible users',
        )
    
    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        if options['show_eligible']:
            self.show_eligible_users()
            return
        
        if options['user_id']:
            self.reset_specific_user_id(options['user_id'], options['dry_run'], options['force'])
        elif options['username']:
            self.reset_specific_username(options['username'], options['dry_run'], options['force'])
        elif options['auto_reset']:
            self.auto_reset_eligible_users(options['dry_run'])
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Enhanced yearly reset command ready!\n"
                    "Options:\n"
                    "  --show-eligible: Show users eligible for reset\n"
                    "  --auto-reset: Reset all eligible users\n"
                    "  --user-id X: Reset specific user\n"
                    "  --username X: Reset specific user\n"
                    "  --dry-run: Preview without changes\n"
                    "  --force: Force reset even if not due"
                )
            )
    
    def show_eligible_users(self):
        """Show all users eligible for yearly reset"""
        yearly_subscribers = self.get_yearly_subscribers()
        eligible_users = []
        
        self.stdout.write(f"\nChecking {len(yearly_subscribers)} yearly subscribers...\n")
        
        for user_data in yearly_subscribers:
            user = user_data['user']
            eligible, reason = UsageTracker.check_yearly_reset_eligible(user)
            
            user_data['eligible'] = eligible
            user_data['reason'] = reason
            
            if eligible:
                eligible_users.append(user_data)
            
            status_color = self.style.SUCCESS if eligible else self.style.WARNING
            self.stdout.write(
                status_color(
                    f"  {user.username:<20} | "
                    f"Days: {user_data['days_since_start']:3d} | "
                    f"Period: {user_data['period']:2d}/12 | "
                    f"Usage: {user_data['current_usage']:3d}/{user_data['limit']:3d} | "
                    f"{'✓ ELIGIBLE' if eligible else '✗ ' + reason}"
                )
            )
        
        self.stdout.write(f"\nSummary: {len(eligible_users)} users eligible for reset")
        return eligible_users
    
    def auto_reset_eligible_users(self, dry_run=False):
        """Automatically reset all eligible yearly subscribers"""
        eligible_users = []
        yearly_subscribers = self.get_yearly_subscribers()
        
        for user_data in yearly_subscribers:
            user = user_data['user']
            eligible, reason = UsageTracker.check_yearly_reset_eligible(user)
            
            if eligible:
                eligible_users.append(user_data)
        
        if not eligible_users:
            self.stdout.write(self.style.WARNING("No users eligible for reset at this time"))
            return
        
        self.stdout.write(f"Found {len(eligible_users)} users eligible for reset")
        
        reset_count = 0
        for user_data in eligible_users:
            user = user_data['user']
            
            if dry_run:
                self.stdout.write(
                    f"DRY RUN: Would reset {user.username} "
                    f"(period {user_data['period']}/12, usage: {user_data['current_usage']}/{user_data['limit']})"
                )
                reset_count += 1
            else:
                try:
                    if UsageTracker.reset_usage(user):
                        # Mark reset as completed
                        UsageTracker.mark_yearly_reset_complete(user, user_data['period'])
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Reset {user.username} - period {user_data['period']}/12 "
                                f"(was: {user_data['current_usage']}/{user_data['limit']})"
                            )
                        )
                        reset_count += 1
                    else:
                        self.stderr.write(f"✗ Failed to reset {user.username}")
                except Exception as e:
                    self.stderr.write(f"✗ Error resetting {user.username}: {str(e)}")
        
        action = "Would reset" if dry_run else "Reset"
        self.stdout.write(
            self.style.SUCCESS(f"\n{action} {reset_count} users")
        )
    
    def reset_specific_user_id(self, user_id, dry_run=False, force=False):
        """Reset specific user by ID"""
        try:
            user = User.objects.get(id=user_id)
            self.reset_user(user, dry_run, force)
        except User.DoesNotExist:
            raise CommandError(f'User with ID {user_id} does not exist')
    
    def reset_specific_username(self, username, dry_run=False, force=False):
        """Reset specific user by username"""
        try:
            user = User.objects.get(username=username)
            self.reset_user(user, dry_run, force)
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist')
    
    def reset_user(self, user, dry_run=False, force=False):
        """Reset individual user with detailed feedback"""
        # Check eligibility
        if not force:
            eligible, reason = UsageTracker.check_yearly_reset_eligible(user)
            if not eligible:
                self.stderr.write(
                    f"User {user.username} not eligible for reset: {reason}"
                )
                return
        
        # Get current usage data
        usage_data = UsageTracker.get_usage_data(user)
        subscription_info = self.get_user_subscription_info(user)
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"DRY RUN: Would reset usage for {user.username}\n"
                    f"  Subscription: {subscription_info['plan_type']}\n"
                    f"  Started: {subscription_info['start_date']}\n"
                    f"  Days active: {subscription_info['days_active']}\n"
                    f"  Current period: {subscription_info['period']}/12\n"
                    f"  Current usage: {usage_data['current']}/{usage_data['limit']}"
                )
            )
        else:
            try:
                if UsageTracker.reset_usage(user):
                    UsageTracker.mark_yearly_reset_complete(user, subscription_info['period'])
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Successfully reset {user.username}\n"
                            f"  Previous usage: {usage_data['current']}/{usage_data['limit']}\n"
                            f"  Reset period: {subscription_info['period']}/12\n"
                            f"  Subscription started: {subscription_info['start_date']}"
                        )
                    )
                else:
                    self.stderr.write(f"✗ Failed to reset usage for {user.username}")
            except Exception as e:
                self.stderr.write(f"✗ Error resetting {user.username}: {str(e)}")
    
    def get_yearly_subscribers(self):
        """Get all yearly subscribers with their data"""
        subscriptions = CustomerSubscription.objects.filter(
            subscription_active=True,
            stripe_subscription_id__isnull=False
        ).select_related('user')
        
        yearly_subscribers = []
        
        for subscription in subscriptions:
            if not subscription.user:
                continue
            
            try:
                stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
                
                # Check if yearly
                if not (stripe_sub.items.data and stripe_sub.items.data[0].plan.interval == 'year'):
                    continue
                
                start_date = datetime.fromtimestamp(stripe_sub.created)
                start_date = timezone.make_aware(start_date)
                now = timezone.now()
                days_since_start = (now - start_date).days
                period = min(days_since_start // 30, 11)
                
                usage_data = UsageTracker.get_usage_data(subscription.user)
                
                yearly_subscribers.append({
                    'user': subscription.user,
                    'subscription': subscription,
                    'start_date': start_date,
                    'days_since_start': days_since_start,
                    'period': period,
                    'current_usage': usage_data['current'],
                    'limit': usage_data['limit'],
                    'stripe_sub_id': subscription.stripe_subscription_id
                })
                
            except Exception as e:
                self.stderr.write(f"Error processing {subscription.user.username}: {str(e)}")
                continue
        
        return yearly_subscribers
    
    def get_user_subscription_info(self, user):
        """Get detailed subscription info for a user"""
        try:
            subscription = CustomerSubscription.objects.filter(
                user=user,
                subscription_active=True
            ).first()
            
            if not subscription or not subscription.stripe_subscription_id:
                return {
                    'plan_type': 'No subscription',
                    'start_date': 'N/A',
                    'days_active': 0,
                    'period': 0
                }
            
            stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
            start_date = datetime.fromtimestamp(stripe_sub.created)
            start_date = timezone.make_aware(start_date)
            now = timezone.now()
            days_active = (now - start_date).days
            period = min(days_active // 30, 11)
            
            plan_type = 'Monthly'
            if stripe_sub.items.data and stripe_sub.items.data[0].plan.interval == 'year':
                plan_type = 'Yearly'
            
            return {
                'plan_type': plan_type,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'days_active': days_active,
                'period': period
            }
            
        except Exception as e:
            return {
                'plan_type': f'Error: {str(e)}',
                'start_date': 'N/A',
                'days_active': 0,
                'period': 0
            }