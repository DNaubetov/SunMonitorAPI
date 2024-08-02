import uuid
from fastapi import Depends, HTTPException, status

from models.api_key import ApiKey


async def authenticate_the_key(api_key: uuid.UUID) -> bool:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in for access"
        )

    get_key = await ApiKey.find_one(ApiKey.key == api_key)
    if not get_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return True
