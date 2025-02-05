from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session 
from passlib.context import CryptContext
from jose import JWTError, jwt
from models import emp, Base, empid_sequence 
import datetime
import os
from typing import List
from fastapi.security import OAuth2PasswordBearer
from google.auth.transport import requests
from fastapi.responses import RedirectResponse
import requests as http_requests
from google.oauth2 import id_token
from google.auth.transport import requests

DATABASE_URL = os.getenv("DATABASE_URL", "#")  
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

#hello
# Add these environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "#")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "#")  # Add your client secret here
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")
FRONTEND_REDIRECT_URI = os.getenv("FRONTEND_REDIRECT_URI", "http://localhost:3000/EmpForm")





app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "SECRECTKEY1234"
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="Emplogin")

ALLOWED_ORG_DOMAINS = ["dpdzero.com"]


class EmployeeCreate(BaseModel):
    name: str
    phno: str
    email: str
    dob: str  
    addr: str
    password: str
    confirm_password: str

    class Config:
        orm_mode = True

    def validate_password(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")

class EmployeeResponse(BaseModel):
    empid: str            
    name: str
    phno: str            
    email: str
    dob: str
    addr: str            

    class Config:
        orm_mode = True

class EmployeeUpdate(BaseModel):
    name: str
    phno: str
    email: str
    dob: str
    addr: str

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()  
    try:
        yield db  
    finally:
        db.close()

class Login(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency to get the current user from the token
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return email


def is_allowed_org(email: str) -> bool:
    domain = email.split('@')[-1]
    return domain in ALLOWED_ORG_DOMAINS


@app.get("/auth/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"{auth_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
    return RedirectResponse(url)

@app.get("/auth/callback")
async def auth_callback(code: str):
    """Handle Google OAuth callback"""
    # Exchange the authorization code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    
    token_response = http_requests.post(token_url, data=token_data)
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get token")
    
    tokens = token_response.json()

    # Verify the ID token
    try:
        id_info = id_token.verify_oauth2_token(
            tokens["id_token"], 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        user_email = id_info.get("email")
        if not user_email or not is_allowed_org(user_email):
            raise HTTPException(status_code=403, detail="Access restricted to authorized organizations")

        # Redirect to frontend
        return RedirectResponse(FRONTEND_REDIRECT_URI)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token")
    


@app.post("/EmpForm", response_model=EmployeeResponse)
def emp_data(emp_data: EmployeeCreate, db: SessionLocal = Depends(get_db)):
    try:
        emp_data.validate_password()

        hashed_password = hash_password(emp_data.password)

        result = db.execute(text("SELECT nextval('empid_seq')"))
        next_empid = result.fetchone()[0]
        empid = f'E{next_empid:03d}'

        db_emp = emp(
            empid=empid,
            name=emp_data.name,
            phno=emp_data.phno,
            email=emp_data.email,
            dob=emp_data.dob,
            addr=emp_data.addr,
            password=hashed_password
        )
        db.add(db_emp)
        db.commit()
        db.refresh(db_emp)
        return db_emp
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    


@app.post("/Emplogin", response_model=Token)
def login(user: Login, db: SessionLocal = Depends(get_db)):
    db_user = db.query(emp).filter(emp.email == user.email).first()
    if db_user is None or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}



@app.get("/EmpList", response_model=List[EmployeeResponse])
def get_employees(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
        employees = db.query(emp).all()
        return employees  
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/logout")
async def logout(current_user: str = Depends(get_current_user)):
    return {"message" : "Successfully logged out"}


@app.get("/employee/{empid}", response_model=EmployeeResponse)
async def get_employee(empid: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    # Fetch employee by empid
    db_employee = db.query(emp).filter(emp.empid == empid).first()
    
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return db_employee


@app.put("/employee/{empid}", response_model=EmployeeResponse)
async def update_employee(
    empid: str,
    employee: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    # Get the employee record
    db_employee = db.query(emp).filter(emp.empid == empid).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if the current user is updating their own record
    if db_employee.email != current_user:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update other employee's data"
        )
    
    # Update the employee data
    for key, value in employee.dict().items():
        setattr(db_employee, key, value)
    
    try:
        db.commit()
        db.refresh(db_employee)
        return db_employee
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/employee/{empid}")
async def delete_employee(
    empid: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    print(f"Attempting to delete employee with ID: {empid}")  # Debug log
    print(f"Current user email: {current_user}")  # Debug log
    
    # Get the employee record
    db_employee = db.query(emp).filter(emp.empid == empid).first()
    
    if not db_employee:
        print(f"Employee not found with ID: {empid}")  # Debug log
        raise HTTPException(status_code=404, detail="Employee not found")
    
    print(f"Found employee email: {db_employee.email}")  # Debug log
    
    # Check if the current user is deleting their own record
    if db_employee.email != current_user:
        print("Authorization failed - emails don't match")  # Debug log
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete other employee's data"
        )
    
    try:
        print("Attempting database deletion")  # Debug log
        db.delete(db_employee)
        db.commit()
        print("Deletion successful")  # Debug log
        return {"message": "Employee successfully deleted"}
    except Exception as e:
        print(f"Error during deletion: {str(e)}")  # Debug log
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    





