from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.account.signals import user_signed_up

User = get_user_model()

@receiver(user_signed_up)
def handle_user_signup(request, user, **kwargs):
    """
    Handler for when a user signs up.
    Can be used to create additional user-related objects or send welcome emails.
    """
    # Example of adding default role (if not already set)
    if not user.role:
        user.role = 'user'
        user.save(update_fields=['role'])
    
    # Here you can add other initialization code
    # For example, sending welcome notifications or emails
        
        