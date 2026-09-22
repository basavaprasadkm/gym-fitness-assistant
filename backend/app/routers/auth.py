from fastapi import APIRouter, HTTPException, status, Depends

from app.models.schemas import UserCreate, UserLogin, Token, UserProfileOut
from app.database import get_supabase
from app.utils.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    supabase = get_supabase()

    existing = await supabase.table("users").select("id").eq("email", user.email).maybe_single().execute()
    if existing and existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")

    doc = user.model_dump()
    doc["password"] = hash_password(user.password)

    result = await supabase.table("users").insert(doc).execute()
    new_user = result.data[0]

    token = create_access_token({"sub": new_user["id"]})
    return Token(access_token=token)


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    supabase = get_supabase()

    resp = await supabase.table("users").select("*").eq("email", credentials.email).maybe_single().execute()
    user = resp.data if resp else None
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token({"sub": user["id"]})
    return Token(access_token=token)


@router.get("/me", response_model=UserProfileOut)
async def get_me(user: dict = Depends(get_current_user)):
    """Returns the logged-in user's own profile, including their admin flag -
    the frontend calls this once after login to decide whether to show the
    Admin page and to greet the user by name on their dashboard."""
    return user
