from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        # Check if the user is authenticated 
        if 'user_id' in session:
            return route_function(*args, **kwargs)
        else:
            flash('Please log in first', 'danger') 
            return redirect(url_for('login'))  # Redirect to the login page if not authenticated
    return wrapper
