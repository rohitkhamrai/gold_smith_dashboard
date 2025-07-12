from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, date as DateType
from decimal import Decimal

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    notes: Optional[str] = None

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    customer_name: str
    date: str = Field(default_factory=lambda: DateType.today().isoformat())
    work_description: str
    gold_in: float = 0.0  # grams received from customer
    gold_out: float = 0.0  # grams given back to customer
    cash_in: float = 0.0  # money received from customer
    labour_charge: float = 0.0  # labour charges
    remarks: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TransactionCreate(BaseModel):
    customer_id: str
    work_description: str
    gold_in: float = 0.0
    gold_out: float = 0.0
    cash_in: float = 0.0
    labour_charge: float = 0.0
    remarks: Optional[str] = None
    date: Optional[str] = None

class Job(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    customer_name: str
    work_description: str
    status: str  # "In Progress", "Completed", "Delivered"
    expected_delivery: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class JobCreate(BaseModel):
    customer_id: str
    work_description: str
    status: str = "In Progress"
    expected_delivery: Optional[str] = None

class DashboardStats(BaseModel):
    total_gold_balance: float
    total_money_balance: float
    active_jobs_count: int
    total_customers: int
    total_transactions: int

# Customer Routes
@api_router.post("/customers", response_model=Customer)
async def create_customer(customer: CustomerCreate):
    customer_dict = customer.dict()
    customer_obj = Customer(**customer_dict)
    await db.customers.insert_one(customer_obj.dict())
    return customer_obj

@api_router.get("/customers", response_model=List[Customer])
async def get_customers():
    customers = await db.customers.find().sort("name", 1).to_list(1000)
    return [Customer(**customer) for customer in customers]

@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    customer = await db.customers.find_one({"id": customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return Customer(**customer)

@api_router.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: str, customer_update: CustomerCreate):
    result = await db.customers.update_one(
        {"id": customer_id}, 
        {"$set": customer_update.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    updated_customer = await db.customers.find_one({"id": customer_id})
    return Customer(**updated_customer)

@api_router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: str):
    # Check if customer has transactions
    transactions = await db.transactions.find({"customer_id": customer_id}).to_list(10)
    if transactions:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete customer. Customer has {len(transactions)} transaction(s). Delete transactions first."
        )
    
    # Check if customer has jobs
    jobs = await db.jobs.find({"customer_id": customer_id}).to_list(10)
    if jobs:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete customer. Customer has {len(jobs)} job(s). Delete jobs first."
        )
    
    result = await db.customers.delete_one({"id": customer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}

@api_router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str):
    result = await db.transactions.delete_one({"id": transaction_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}

@api_router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    result = await db.jobs.delete_one({"id": job_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}

# Transaction Routes
@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate):
    # Get customer details
    customer = await db.customers.find_one({"id": transaction.customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    transaction_dict = transaction.dict()
    if transaction_dict["date"] is None:
        transaction_dict["date"] = DateType.today().isoformat()
    
    transaction_dict["customer_name"] = customer["name"]
    transaction_obj = Transaction(**transaction_dict)
    await db.transactions.insert_one(transaction_obj.dict())
    return transaction_obj

@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions(customer_id: Optional[str] = None):
    query = {}
    if customer_id:
        query["customer_id"] = customer_id
    
    transactions = await db.transactions.find(query).sort("date", -1).to_list(1000)
    return [Transaction(**transaction) for transaction in transactions]

@api_router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: str):
    transaction = await db.transactions.find_one({"id": transaction_id})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return Transaction(**transaction)

# Job Routes
@api_router.post("/jobs", response_model=Job)
async def create_job(job: JobCreate):
    # Get customer details
    customer = await db.customers.find_one({"id": job.customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    job_dict = job.dict()
    job_dict["customer_name"] = customer["name"]
    job_obj = Job(**job_dict)
    await db.jobs.insert_one(job_obj.dict())
    return job_obj

@api_router.get("/jobs", response_model=List[Job])
async def get_jobs(status: Optional[str] = None):
    query = {}
    if status:
        query["status"] = status
    
    jobs = await db.jobs.find(query).sort("created_at", -1).to_list(1000)
    return [Job(**job) for job in jobs]

@api_router.put("/jobs/{job_id}", response_model=Job)
async def update_job_status(job_id: str, status: str):
    result = await db.jobs.update_one(
        {"id": job_id}, 
        {"$set": {"status": status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    
    updated_job = await db.jobs.find_one({"id": job_id})
    return Job(**updated_job)

# Balance calculation endpoint
@api_router.get("/customer/{customer_id}/balance")
async def get_customer_balance(customer_id: str):
    transactions = await db.transactions.find({"customer_id": customer_id}).to_list(1000)
    
    total_gold_balance = 0.0
    total_money_balance = 0.0
    
    for transaction in transactions:
        # Gold balance: gold_in (received from customer) - gold_out (given back to customer)
        total_gold_balance += transaction.get("gold_in", 0) - transaction.get("gold_out", 0)
        # Money balance: cash_in (received) + labour_charge (earned)
        total_money_balance += transaction.get("cash_in", 0) + transaction.get("labour_charge", 0)
    
    return {
        "customer_id": customer_id,
        "gold_balance": round(total_gold_balance, 3),
        "money_balance": round(total_money_balance, 2)
    }

# Dashboard stats
@api_router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats():
    # Get all transactions for balance calculation
    transactions = await db.transactions.find().to_list(10000)
    
    total_gold_balance = 0.0
    total_money_balance = 0.0
    
    for transaction in transactions:
        total_gold_balance += transaction.get("gold_in", 0) - transaction.get("gold_out", 0)
        total_money_balance += transaction.get("cash_in", 0) + transaction.get("labour_charge", 0)
    
    # Count active jobs
    active_jobs = await db.jobs.count_documents({"status": {"$in": ["In Progress", "Completed"]}})
    
    # Count customers and transactions
    total_customers = await db.customers.count_documents({})
    total_transactions = await db.transactions.count_documents({})
    
    return DashboardStats(
        total_gold_balance=round(total_gold_balance, 3),
        total_money_balance=round(total_money_balance, 2),
        active_jobs_count=active_jobs,
        total_customers=total_customers,
        total_transactions=total_transactions
    )

# Basic health check
@api_router.get("/")
async def root():
    return {"message": "Goldsmith Ledger API"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()