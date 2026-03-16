from fastapi import APIRouter, HTTPException, status, Depends
from database import users_collection
from models import UserCreate, UserLogin, Token
from auth import hash_password, verify_password, create_access_token
from dependencies import get_current_user

router = APIRouter()


@router.post("/signup", response_model=Token)
async def signup(user: UserCreate):
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    ca_id = None
    firm_name = ""

    # STRICT ROLE ROUTING
    if user.role == "Clerk":
        if not user.admin_email:
            raise HTTPException(
                status_code=400, detail="Clerks must provide their Admin's email to join a firm.")
        admin_user = await users_collection.find_one({"email": user.admin_email, "role": "Admin"})
        if not admin_user:
            raise HTTPException(
                status_code=404, detail="Admin email not found. Check the email address.")

        ca_id = str(admin_user["_id"])
        firm_name = admin_user.get("firm_name", "CA Firm")
    else:
        if not user.firm_name:
            raise HTTPException(
                status_code=400, detail="Admins must provide a Firm Name.")
        firm_name = user.firm_name

    new_user = {
        "name": user.name,
        "email": user.email,
        "password_hash": hash_password(user.password),
        "firm_name": firm_name,
        "role": user.role,
        "ca_id": ca_id  # Will be updated for Admins after insertion
    }

    result = await users_collection.insert_one(new_user)

    # If Admin, their own ID is the firm's CA ID
    if user.role == "Admin":
        ca_id = str(result.inserted_id)
        await users_collection.update_one({"_id": result.inserted_id}, {"$set": {"ca_id": ca_id}})

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    db_user = await users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(
            status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    return {
        "name": current_user["name"],
        "email": current_user["email"],
        "firm_name": current_user.get("firm_name", "CA Firm"),
        "role": current_user.get("role", "Admin"),
        "ca_id": current_user.get("ca_id", str(current_user["_id"]))
    }
