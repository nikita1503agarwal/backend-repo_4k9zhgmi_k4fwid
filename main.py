import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

# Database helpers
from database import db, create_document, get_documents

app = FastAPI(title="CustomPrint Studio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------
# Models (request/response)
# -----------------------
class EnquiryIn(BaseModel):
    name: str = Field(...)
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    product_type: str = Field(..., description="2D Laser-cut | 3D Trophy | 3D Mockup | Other")
    quantity: Optional[int] = Field(None, ge=1)
    budget_range: Optional[str] = None
    message: str
    reference_url: Optional[str] = None

class EnquiryOut(BaseModel):
    id: str
    created_at: datetime

class ProductOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    category: str
    image: Optional[str] = None
    featured: bool = False


# -----------------------
# Utility
# -----------------------

def _to_product_out(doc) -> ProductOut:
    return ProductOut(
        id=str(doc.get("_id")),
        title=doc.get("title", "Untitled"),
        description=doc.get("description"),
        price=doc.get("price"),
        category=doc.get("category", "General"),
        image=doc.get("image"),
        featured=bool(doc.get("featured", False)),
    )


# -----------------------
# Lifecycle: seed featured products if empty
# -----------------------
@app.on_event("startup")
def seed_products_if_needed():
    try:
        if db is None:
            return
        count = db["product"].count_documents({})
        if count == 0:
            demo_products = [
                {
                    "title": "Precision Laser‑Cut Signage",
                    "description": "Crisp edges in acrylic/wood with custom finishes.",
                    "price": 149.0,
                    "category": "2D Laser-cut",
                    "image": "https://images.unsplash.com/photo-1518779578993-ec3579fee39f?q=80&w=1600&auto=format&fit=crop",
                    "featured": True,
                },
                {
                    "title": "3D Trophy – Metallic Finish",
                    "description": "Award‑ready trophies with premium 3D look.",
                    "price": 249.0,
                    "category": "3D Trophy",
                    "image": "https://images.unsplash.com/photo-1513451713350-dee890297c4a?q=80&w=1600&auto=format&fit=crop",
                    "featured": True,
                },
                {
                    "title": "3D‑Style Product Mockup",
                    "description": "Stand‑out visuals for packaging and promos.",
                    "price": 99.0,
                    "category": "3D Mockup",
                    "image": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=80&w=1600&auto=format&fit=crop",
                    "featured": True,
                },
                {
                    "title": "Custom Keychains",
                    "description": "Personalised laser‑cut keychains in bulk.",
                    "price": 5.0,
                    "category": "2D Laser-cut",
                    "image": "https://images.unsplash.com/photo-1520975922133-0f775525ae37?q=80&w=1600&auto=format&fit=crop",
                    "featured": False,
                },
            ]
            for p in demo_products:
                p["created_at"] = datetime.utcnow()
                p["updated_at"] = datetime.utcnow()
            db["product"].insert_many(demo_products)
    except Exception:
        # Silent fail if DB not configured
        pass


# -----------------------
# Basic routes
# -----------------------
@app.get("/")
def read_root():
    return {"message": "CustomPrint Studio API running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


# -----------------------
# Health / DB test
# -----------------------
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# -----------------------
# Products
# -----------------------
@app.get("/api/products", response_model=List[ProductOut])
def list_products(featured: Optional[bool] = None, category: Optional[str] = None):
    if db is None:
        # Return a minimal fallback when DB not configured
        fallback = [
            {
                "_id": "0",
                "title": "Sample Product",
                "description": "Configure DATABASE_URL and DATABASE_NAME to load real items.",
                "category": "General",
                "image": None,
                "featured": True,
            }
        ]
        return [_to_product_out(doc) for doc in fallback]

    query = {}
    if featured is not None:
        query["featured"] = bool(featured)
    if category:
        query["category"] = category

    docs = list(db["product"].find(query).sort("created_at", -1))
    return [_to_product_out(doc) for doc in docs]


# -----------------------
# Enquiries
# -----------------------
@app.post("/api/enquiries", response_model=EnquiryOut, status_code=201)
def create_enquiry(payload: EnquiryIn):
    try:
        inserted_id = create_document("enquiry", payload)
        return EnquiryOut(id=inserted_id, created_at=datetime.utcnow())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
