from fastapi import APIRouter

router = APIRouter(redirect_slashes=False, prefix="/users", tags=['Users'])
