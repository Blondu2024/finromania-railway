"""Portfolio routes pentru FinRomania"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import uuid
from config.database import get_database
from routes.auth import require_auth

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

class PortfolioTransaction(BaseModel):
    symbol: str
    type: str  # 'bvb' or 'global'
    name: Optional[str] = None
    action: str  # 'buy' or 'sell'
    quantity: int
    price: float

class PortfolioHolding(BaseModel):
    symbol: str
    type: str
    name: Optional[str] = None
    quantity: int
    avg_price: float
    total_invested: float
    current_value: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None

@router.get("/holdings", response_model=List[PortfolioHolding])
async def get_holdings(user: dict = Depends(require_auth)):
    """Get portfolio holdings"""
    db = await get_database()
    holdings = await db.portfolio_holdings.find(
        {"user_id": user["user_id"], "quantity": {"$gt": 0}},
        {"_id": 0}
    ).to_list(100)
    
    # Calculate current values
    for holding in holdings:
        if holding["type"] == "bvb":
            stock = await db.stocks_bvb.find_one({"symbol": holding["symbol"]}, {"_id": 0})
        else:
            stock = await db.stocks_global.find_one({"symbol": holding["symbol"]}, {"_id": 0})
        
        if stock and stock.get("price"):
            holding["current_value"] = holding["quantity"] * stock["price"]
            holding["profit_loss"] = holding["current_value"] - holding["total_invested"]
            if holding["total_invested"] > 0:
                holding["profit_loss_percent"] = (holding["profit_loss"] / holding["total_invested"]) * 100
    
    return holdings

@router.get("/summary")
async def get_portfolio_summary(user: dict = Depends(require_auth)):
    """Get portfolio summary"""
    db = await get_database()
    holdings = await db.portfolio_holdings.find(
        {"user_id": user["user_id"], "quantity": {"$gt": 0}},
        {"_id": 0}
    ).to_list(100)
    
    total_invested = 0
    total_current = 0
    
    for holding in holdings:
        total_invested += holding.get("total_invested", 0)
        
        if holding["type"] == "bvb":
            stock = await db.stocks_bvb.find_one({"symbol": holding["symbol"]}, {"_id": 0})
        else:
            stock = await db.stocks_global.find_one({"symbol": holding["symbol"]}, {"_id": 0})
        
        if stock and stock.get("price"):
            total_current += holding["quantity"] * stock["price"]
    
    profit_loss = total_current - total_invested
    profit_loss_percent = (profit_loss / total_invested * 100) if total_invested > 0 else 0
    
    return {
        "total_invested": round(total_invested, 2),
        "total_current": round(total_current, 2),
        "profit_loss": round(profit_loss, 2),
        "profit_loss_percent": round(profit_loss_percent, 2),
        "holdings_count": len(holdings)
    }

@router.post("/transaction")
async def add_transaction(txn: PortfolioTransaction, user: dict = Depends(require_auth)):
    """Add buy/sell transaction"""
    db = await get_database()
    
    # Record transaction
    transaction = {
        "id": f"txn_{uuid.uuid4().hex[:12]}",
        "user_id": user["user_id"],
        "symbol": txn.symbol,
        "type": txn.type,
        "name": txn.name,
        "action": txn.action,
        "quantity": txn.quantity,
        "price": txn.price,
        "total": txn.quantity * txn.price,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.portfolio_transactions.insert_one(transaction)
    
    # Update holdings
    existing = await db.portfolio_holdings.find_one({
        "user_id": user["user_id"],
        "symbol": txn.symbol,
        "type": txn.type
    })
    
    if txn.action == "buy":
        if existing:
            new_quantity = existing["quantity"] + txn.quantity
            new_total = existing["total_invested"] + (txn.quantity * txn.price)
            new_avg = new_total / new_quantity if new_quantity > 0 else 0
            
            await db.portfolio_holdings.update_one(
                {"user_id": user["user_id"], "symbol": txn.symbol, "type": txn.type},
                {"$set": {
                    "quantity": new_quantity,
                    "total_invested": new_total,
                    "avg_price": new_avg
                }}
            )
        else:
            await db.portfolio_holdings.insert_one({
                "user_id": user["user_id"],
                "symbol": txn.symbol,
                "type": txn.type,
                "name": txn.name,
                "quantity": txn.quantity,
                "avg_price": txn.price,
                "total_invested": txn.quantity * txn.price
            })
    
    elif txn.action == "sell":
        if not existing or existing["quantity"] < txn.quantity:
            raise HTTPException(status_code=400, detail="Insufficient holdings")
        
        new_quantity = existing["quantity"] - txn.quantity
        sell_ratio = txn.quantity / existing["quantity"]
        new_total = existing["total_invested"] * (1 - sell_ratio)
        
        await db.portfolio_holdings.update_one(
            {"user_id": user["user_id"], "symbol": txn.symbol, "type": txn.type},
            {"$set": {
                "quantity": new_quantity,
                "total_invested": new_total
            }}
        )
    
    return {"message": "Transaction recorded", "transaction_id": transaction["id"]}

@router.get("/transactions")
async def get_transactions(user: dict = Depends(require_auth), limit: int = 50):
    """Get transaction history"""
    db = await get_database()
    transactions = await db.portfolio_transactions.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return transactions
