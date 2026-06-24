# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import Column, String, Integer, Boolean, Float
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import Base, engine, get_db
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

# Initialize the FastAPI application
app = FastAPI()

# Define the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Define the user model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)

# Define the property model
class Property(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    location = Column(String)
    price = Column(Float)
    status = Column(String)

# Define the token model
class Token(BaseModel):
    access_token: str
    token_type: str

# Define the token data model
class TokenData(BaseModel):
    username: str | None = None

# Initialize the password context
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

# Function to get the current user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# Function to get the current active user
def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Function to verify password
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Function to get password hash
def get_password_hash(password: str):
    return pwd_context.hash(password)

# Function to authenticate user
def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

# Function to create access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "secret_key", algorithm="HS256")
    return encoded_jwt

# Login endpoint
@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password, get_db())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Register endpoint
@app.post("/register")
async def register(username: str, email: str, password: str, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(password)
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(username=username, email=email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

# Dashboard endpoint
@app.get("/dashboard")
async def dashboard(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    total_properties = db.query(Property).count()
    active_listings = db.query(Property).filter(Property.status == "Available").count()
    total_revenue = db.query(Property).filter(Property.status == "Sold").count()
    properties = db.query(Property).all()
    return {
        "total_properties": total_properties,
        "active_listings": active_listings,
        "total_revenue": total_revenue,
        "properties": properties,
    }

# Add property endpoint
@app.post("/add_property")
async def add_property(name: str, location: str, price: float, status: str, db: Session = Depends(get_db)):
    new_property = Property(name=name, location=location, price=price, status=status)
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return {"message": "Property added successfully"}

# Get properties endpoint
@app.get("/properties")
async def get_properties(db: Session = Depends(get_db)):
    properties = db.query(Property).all()
    return properties

# Update property endpoint
@app.put("/update_property/{property_id}")
async def update_property(property_id: int, name: str, location: str, price: float, status: str, db: Session = Depends(get_db)):
    property_to_update = db.query(Property).filter(Property.id == property_id).first()
    if not property_to_update:
        raise HTTPException(status_code=404, detail="Property not found")
    property_to_update.name = name
    property_to_update.location = location
    property_to_update.price = price
    property_to_update.status = status
    db.commit()
    db.refresh(property_to_update)
    return {"message": "Property updated successfully"}

# Delete property endpoint
@app.delete("/delete_property/{property_id}")
async def delete_property(property_id: int, db: Session = Depends(get_db)):
    property_to_delete = db.query(Property).filter(Property.id == property_id).first()
    if not property_to_delete:
        raise HTTPException(status_code=404, detail="Property not found")
    db.delete(property_to_delete)
    db.commit()
    return {"message": "Property deleted successfully"}