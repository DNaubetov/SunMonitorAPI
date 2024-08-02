from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from auth.role_validator import has_role
from database.connection import Database
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.users import User, TokenResponse, RoleEnum

user_router = APIRouter(
    tags=["User"],
)

user_database = Database(User)
hash_password = HashPassword()


@user_router.post("/signup")
async def sign_user_up(user: User, admin: User = Depends(has_role(RoleEnum.admin))) -> dict:
    if user.role == 'super_admin':
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Вы не имеете право"
        )

    user_exist = await User.find_one(User.name == user.name)

    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email provided exists already."
        )
    hashed_password = hash_password.create_hash(user.password)
    user.password = hashed_password
    await user_database.save(user)
    return {
        "message": "User created successfully"
    }


@user_router.post("/signin", response_model=TokenResponse)
async def sign_user_in(user: OAuth2PasswordRequestForm = Depends()) -> dict:
    # user.username = user.username.lower()
    user_exist = await User.find_one(User.name == user.username.lower())
    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with email does not exist."
        )
    if hash_password.verify_hash(user.password, user_exist.password):
        access_token = create_access_token(user_exist.name)
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed."
    )


@user_router.post("/all")
async def get_all_user_up(user: User = Depends(has_role())):
    user_exist = await User.find_all().to_list()
    return user_exist
