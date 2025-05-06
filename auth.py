from fastapi import Depends, HTTPException, Request, status
from werkzeug.security import generate_password_hash, check_password_hash
import crud, database

# Password utils
def get_password_hash(pw): return generate_password_hash(pw)
def verify_password(pw, h): return check_password_hash(h, pw)

# Dependency to get current user
async def get_current_user(request: Request):
    uid = request.session.get('user_id')
    if not uid:
        raise HTTPException(status_code=status.HTTP_302_FOUND, headers={'Location':'/user/login'})
    user = crud.get_user_by_id(uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_302_FOUND, headers={'Location':'/user/login'})
    return user

# Admin dependency
async def get_current_admin(request: Request):
    if not request.session.get('is_admin'):
        raise HTTPException(status_code=status.HTTP_302_FOUND, headers={'Location':'/admin/login'})
    return True
