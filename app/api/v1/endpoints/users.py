from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

router = APIRouter()


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    is_active: bool = Field(True, description="Is user active")


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class User(UserBase):
    """User schema with ID."""
    id: int = Field(..., description="User ID")

    class Config:
        from_attributes = True


# In-memory storage (replace with database in production)
users_db: dict[int, User] = {}
next_id = 1


@router.get("/", response_model=list[User])
async def get_users(skip: int = 0, limit: int = 100):
    """Get all users with pagination."""
    users = list(users_db.values())
    return users[skip : skip + limit]


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get a specific user by ID."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return users_db[user_id]


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Create a new user."""
    global next_id

    # Check if email already exists
    for existing_user in users_db.values():
        if existing_user.email == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        if existing_user.username == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    # In production, hash the password before storing
    user_data = user.model_dump(exclude={"password"})
    new_user = User(id=next_id, **user_data)
    users_db[next_id] = new_user
    next_id += 1
    return new_user


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate):
    """Update an existing user."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    existing_user = users_db[user_id]
    update_data = user.model_dump(exclude_unset=True)

    updated_user = existing_user.model_copy(update=update_data)
    users_db[user_id] = updated_user

    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """Delete a user."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    del users_db[user_id]
