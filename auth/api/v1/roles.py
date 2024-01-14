from fastapi import APIRouter

router = APIRouter(redirect_slashes=False, prefix="/roles", tags=['Roles'])
