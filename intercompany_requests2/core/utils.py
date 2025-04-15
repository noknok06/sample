import os
import uuid
from django.utils.text import slugify

def get_file_path(instance, filename):
    """
    Generate a unique filename for uploads.
    
    Args:
        instance: The model instance this file is attached to
        filename: Original filename
        
    Returns:
        String path where file should be saved
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    
    # Get the model name to use as subdirectory
    model_name = instance.__class__.__name__.lower()
    
    return os.path.join(f'uploads/{model_name}/', filename)

def user_has_permission(user, permission_type, obj=None):
    """
    Check if user has permission to perform action.
    
    Args:
        user: User object
        permission_type: String (view, add, change, delete)
        obj: Optional object to check permission against
        
    Returns:
        Boolean indicating if user has permission
    """
    # Admin users have all permissions
    if user.is_admin:
        return True
    
    # Managers have certain permissions
    if user.is_manager:
        if permission_type in ['view', 'add']:
            return True
        
        # For change/delete, check if object belongs to user's company
        if obj and hasattr(obj, 'company'):
            return obj.company == user.company
        
        # For user objects, check if they're in same company
        if obj and hasattr(obj, 'email'):  # Assuming it's a User object
            return obj.company == user.company
    
    # Regular users can view and add certain things
    if permission_type == 'view':
        # Regular users can view objects in their company
        if obj and hasattr(obj, 'company'):
            return obj.company == user.company
        
        # For user objects, check if they're in same company
        if obj and hasattr(obj, 'email'):
            return obj.company == user.company
    
    # By default, deny permission
    return False