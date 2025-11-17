import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from database import db, create_document, get_documents
from schemas import StoryOrder, Tier, Character, OrderStatus

app = FastAPI(title="Custom Kids Stories API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Custom Kids Stories Backend Running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# Static tiers
TIERS: List[Tier] = [
    Tier(name="Spark", price=19.0, features=["1 character", "500 words", "PDF"], delivery_days=3),
    Tier(name="Glow", price=39.0, features=["2 characters", "800 words", "3 illustrations", "PDF"], delivery_days=5),
    Tier(name="Shine", price=69.0, features=["Up to 3 characters", "1200 words", "5 illustrations", "PDF + ePub"], delivery_days=7),
    Tier(name="Supernova", price=129.0, features=["Up to 4 characters", "2000 words", "8 illustrations", "PDF + ePub + Web"], delivery_days=10),
]


@app.get("/api/tiers", response_model=List[Tier])
def list_tiers():
    return TIERS


# Demo character catalog (a subset; can be expanded in DB later)
CHARACTERS: List[Character] = [
    Character(key="cinderella", name="Cinderella", era="Fairy Tale", tags=["kindness", "perseverance"]),
    Character(key="little-red-riding-hood", name="Little Red Riding Hood", era="Folk Tale", tags=["bravery", "wisdom"]),
    Character(key="jack-beanstalk", name="Jack (Beanstalk)", era="Folk Tale", tags=["adventure", "curiosity"]),
    Character(key="snow-white", name="Snow White", era="Fairy Tale", tags=["friendship", "courage"]),
]


@app.get("/api/characters", response_model=List[Character])
def list_characters():
    # If we later store in DB, replace with get_documents('character', {...})
    return CHARACTERS


@app.post("/api/orders", response_model=Dict[str, Any])
def create_order(order: StoryOrder):
    try:
        # Persist the order
        inserted_id = create_document("storyorder", order)
        status = OrderStatus(order_id=inserted_id, status="received")
        create_document("orderstatus", status)
        return {"order_id": inserted_id, "status": status.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orders", response_model=List[Dict[str, Any]])
def list_orders():
    try:
        docs = get_documents("storyorder", {}, limit=50)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orders/{order_id}", response_model=OrderStatus)
def get_order_status(order_id: str):
    try:
        # naive lookup
        statuses = get_documents("orderstatus", {"order_id": order_id}, limit=1)
        if not statuses:
            raise HTTPException(status_code=404, detail="Order not found")
        s = statuses[0]
        return OrderStatus(order_id=s.get("order_id"), status=s.get("status"), download_url=s.get("download_url"), preview_images=s.get("preview_images", []))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
