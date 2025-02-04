from fastapi import FastAPI, HTTPException, Depends, status
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

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://shanks:shanks%402003@localhost:5432/empform")  
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

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

    





