"""Portfolio V2 - Trading Simulator Educațional"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid
from config.database import get_database
from routes.auth import require_auth

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

# ============================================
# ENUMS & CONSTANTS
# ============================================

class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"

class PositionType(str, Enum):
    LONG = "long"
    SHORT = "short"

STARTING_CASH = 50000.0  # RON
LEVERAGE_LIMITS = {
    ExperienceLevel.BEGINNER: 2.0,
    ExperienceLevel.INTERMEDIATE: 5.0,
    ExperienceLevel.ADVANCED: 10.0
}

ACHIEVEMENTS = {
    "first_trade": {"name": "Prima Tranzacție", "description": "Ai completat prima tranzacție!"},
    "profitable_trade": {"name": "Profit +10%", "description": "Ai realizat +10% profit pe o poziție!"},
    "stop_loss_saved": {"name": "Salvat de Stop Loss", "description": "Stop Loss-ul tău a prevenit pierderi mari!"},
    "diversified": {"name": "Portofoliu Diversificat", "description": "Ai investit în 5+ acțiuni diferite!"},
    "monthly_profit": {"name": "Lună Profitabilă", "description": "Profit de +5% într-o lună!"},
}

# ============================================
# MODELS
# ============================================

class PortfolioInit(BaseModel):
    experience_level: ExperienceLevel = ExperienceLevel.BEGINNER
    completed_tutorial: bool = False

class TradeOrder(BaseModel):
    symbol: str
    market_type: str  # 'bvb' or 'global'
    position_type: PositionType = PositionType.LONG
    order_type: OrderType = OrderType.MARKET
    quantity: int = Field(gt=0)
    leverage: float = Field(default=1.0, ge=1.0, le=10.0)
    limit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class Position(BaseModel):
    position_id: str
    symbol: str
    name: str
    market_type: str
    position_type: PositionType
    quantity: int
    entry_price: float
    current_price: float
    leverage: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    invested: float
    current_value: float
    pnl: float
    pnl_percent: float
    opened_at: str

# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_current_price(db, symbol: str, market_type: str) -> Optional[float]:
    """Get current price for a symbol"""
    collection = db.stocks_bvb if market_type == "bvb" else db.stocks_global
    stock = await collection.find_one({"symbol": symbol.upper()}, {"_id": 0})
    return stock.get("price") if stock else None

async def check_achievements(db, user_id: str, portfolio_data: dict):
    """Check and award achievements"""
    achievements = portfolio_data.get("achievements", [])
    new_achievements = []
    
    # First trade
    if "first_trade" not in achievements and portfolio_data.get("trades_count", 0) >= 1:
        new_achievements.append("first_trade")
    
    # Diversified portfolio
    positions = portfolio_data.get("open_positions", [])
    unique_symbols = set(p["symbol"] for p in positions)
    if "diversified" not in achievements and len(unique_symbols) >= 5:
        new_achievements.append("diversified")
    
    if new_achievements:
        await db.user_portfolios.update_one(
            {"user_id": user_id},
            {"$addToSet": {"achievements": {"$each": new_achievements}}}
        )
    
    return new_achievements

# ============================================
# ROUTES
# ============================================

@router.post("/init")
async def initialize_portfolio(init_data: PortfolioInit, user: dict = Depends(require_auth)):
    """Initialize demo trading portfolio"""
    db = await get_database()
    
    # Check if already exists
    existing = await db.user_portfolios.find_one({"user_id": user["user_id"]})
    if existing:
        return {"message": "Portfolio already initialized", "portfolio_id": existing.get("portfolio_id")}
    
    portfolio = {
        "portfolio_id": f"port_{uuid.uuid4().hex[:12]}",
        "user_id": user["user_id"],
        "cash": STARTING_CASH,
        "starting_cash": STARTING_CASH,
        "experience_level": init_data.experience_level,
        "completed_tutorial": init_data.completed_tutorial,
        "achievements": [],
        "trades_count": 0,
        "open_positions": [],
        "closed_positions_count": 0,
        "total_pnl": 0.0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.user_portfolios.insert_one(portfolio)
    
    return {
        "message": "Portfolio initialized successfully",
        "portfolio_id": portfolio["portfolio_id"],
        "starting_cash": STARTING_CASH,
        "experience_level": init_data.experience_level
    }

@router.get("/status")
async def get_portfolio_status(user: dict = Depends(require_auth)):
    """Get portfolio status with real-time calculations"""
    db = await get_database()
    
    portfolio = await db.user_portfolios.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not initialized. Call /portfolio/init first")
    
    # Calculate current portfolio value
    open_positions = portfolio.get("open_positions", [])
    total_position_value = 0.0
    margin_used = 0.0
    
    for pos in open_positions:
        current_price = await get_current_price(db, pos["symbol"], pos["market_type"])
        if current_price:
            pos["current_price"] = current_price
            
            # Calculate position value
            pos_value = pos["quantity"] * current_price
            
            # Calculate P&L with LEVERAGE amplification
            if pos["position_type"] == PositionType.LONG:
                # LONG: profit when price goes up
                price_change = current_price - pos["entry_price"]
                pnl = price_change * pos["quantity"] * pos.get("leverage", 1.0)
                pos["current_value"] = pos["invested"] + pnl
            else:  # SHORT
                # SHORT: profit when price goes down
                price_change = pos["entry_price"] - current_price
                pnl = price_change * pos["quantity"] * pos.get("leverage", 1.0)
                pos["current_value"] = pos["invested"] + pnl
            
            pos["pnl"] = pnl
            pos["pnl_percent"] = (pos["pnl"] / pos["invested"]) * 100 if pos["invested"] > 0 else 0
            
            total_position_value += pos["current_value"]
            margin_used += pos["invested"] / pos.get("leverage", 1.0)
    
    cash = portfolio.get("cash", STARTING_CASH)
    total_value = cash + total_position_value
    total_pnl = total_value - STARTING_CASH
    total_pnl_percent = (total_pnl / STARTING_CASH) * 100
    
    return {
        "portfolio_id": portfolio["portfolio_id"],
        "demo_mode": True,
        "experience_level": portfolio["experience_level"],
        "max_leverage": LEVERAGE_LIMITS[portfolio["experience_level"]],
        "cash": round(cash, 2),
        "margin_used": round(margin_used, 2),
        "margin_available": round(cash - margin_used, 2),
        "positions_value": round(total_position_value, 2),
        "total_value": round(total_value, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_percent": round(total_pnl_percent, 2),
        "starting_cash": STARTING_CASH,
        "open_positions_count": len(open_positions),
        "open_positions": open_positions,
        "trades_count": portfolio.get("trades_count", 0),
        "achievements": portfolio.get("achievements", []),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

@router.post("/trade")
async def execute_trade(order: TradeOrder, user: dict = Depends(require_auth)):
    """Execute a trade with educational checks and realistic slippage"""
    db = await get_database()
    
    portfolio = await db.user_portfolios.find_one({"user_id": user["user_id"]})
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not initialized")
    
    # Check leverage limits
    max_leverage = LEVERAGE_LIMITS[portfolio["experience_level"]]
    if order.leverage > max_leverage:
        raise HTTPException(
            status_code=403,
            detail=f"Leverage {order.leverage}x exceeds your limit of {max_leverage}x for {portfolio['experience_level']} level"
        )
    
    # Get current price WITH slippage simulation
    # Import at function level to avoid circular imports
    import httpx
    async with httpx.AsyncClient() as client:
        # Get live quote with bid/ask
        import os
        backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        response = await client.get(
            f"{backend_url}/api/live/quote/{order.symbol}?market_type={order.market_type}",
            timeout=10
        )
        
        if response.status_code == 200:
            quote = response.json()
            # Use ASK price for LONG (buying), BID price for SHORT (selling to open)
            if order.position_type == PositionType.LONG:
                execution_price = quote["ask"]  # Buy at higher price (realistic!)
            else:
                execution_price = quote["bid"]  # Sell at lower price
            
            current_price = quote["price"]
            spread = quote["spread"]
        else:
            # Fallback to database price
            current_price = await get_current_price(db, order.symbol, order.market_type)
            if not current_price:
                raise HTTPException(status_code=404, detail=f"Symbol {order.symbol} not found")
            execution_price = current_price
            spread = 0
    if not current_price:
        raise HTTPException(status_code=404, detail=f"Symbol {order.symbol} not found")
    
    # Get stock name
    collection = db.stocks_bvb if order.market_type == "bvb" else db.stocks_global
    stock = await collection.find_one({"symbol": order.symbol.upper()}, {"_id": 0})
    stock_name = stock.get("name", order.symbol) if stock else order.symbol
    
    # Calculate costs
    if order.order_type == OrderType.LIMIT and order.limit_price:
        execution_price = order.limit_price
    else:
        execution_price = current_price
    
    position_value = order.quantity * execution_price
    margin_required = position_value / order.leverage
    
    # Check cash availability
    if portfolio["cash"] < margin_required:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient cash. Required: {margin_required:.2f} RON, Available: {portfolio['cash']:.2f} RON"
        )
    
    # Create position
    position = {
        "position_id": f"pos_{uuid.uuid4().hex[:12]}",
        "symbol": order.symbol.upper(),
        "name": stock_name,
        "market_type": order.market_type,
        "position_type": order.position_type,
        "quantity": order.quantity,
        "entry_price": execution_price,
        "current_price": current_price,
        "leverage": order.leverage,
        "stop_loss": order.stop_loss,
        "take_profit": order.take_profit,
        "invested": margin_required,
        "current_value": position_value,
        "pnl": 0.0,
        "pnl_percent": 0.0,
        "opened_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Update portfolio
    new_cash = portfolio["cash"] - margin_required
    trades_count = portfolio.get("trades_count", 0) + 1
    
    await db.user_portfolios.update_one(
        {"user_id": user["user_id"]},
        {
            "$set": {
                "cash": new_cash,
                "trades_count": trades_count,
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            "$push": {"open_positions": position}
        }
    )
    
    # Record transaction
    transaction = {
        "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
        "user_id": user["user_id"],
        "action": "open_position",
        "position_id": position["position_id"],
        "symbol": order.symbol.upper(),
        "position_type": order.position_type,
        "quantity": order.quantity,
        "price": execution_price,
        "leverage": order.leverage,
        "margin": margin_required,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.portfolio_transactions.insert_one(transaction)
    
    # Check achievements
    portfolio["trades_count"] = trades_count
    new_achievements = await check_achievements(db, user["user_id"], portfolio)
    
    return {
        "message": "Trade executed successfully",
        "position_id": position["position_id"],
        "execution_price": execution_price,
        "margin_used": margin_required,
        "remaining_cash": round(new_cash, 2),
        "new_achievements": new_achievements
    }

@router.post("/close/{position_id}")
async def close_position(position_id: str, user: dict = Depends(require_auth)):
    """Close an open position"""
    db = await get_database()
    
    portfolio = await db.user_portfolios.find_one({"user_id": user["user_id"]})
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Find position
    position = None
    for pos in portfolio.get("open_positions", []):
        if pos["position_id"] == position_id:
            position = pos
            break
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    # Get current price
    current_price = await get_current_price(db, position["symbol"], position["market_type"])
    if not current_price:
        raise HTTPException(status_code=404, detail="Cannot get current price")
    
    # Calculate P&L
    position_value = position["quantity"] * current_price
    
    if position["position_type"] == PositionType.LONG:
        pnl = position_value - (position["entry_price"] * position["quantity"])
    else:  # SHORT
        pnl = (position["entry_price"] * position["quantity"]) - position_value
    
    # Return cash (invested margin + P&L)
    cash_return = position["invested"] + pnl
    new_cash = portfolio["cash"] + cash_return
    
    # Update portfolio - remove from open positions
    await db.user_portfolios.update_one(
        {"user_id": user["user_id"]},
        {
            "$pull": {"open_positions": {"position_id": position_id}},
            "$set": {
                "cash": new_cash,
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            "$inc": {
                "closed_positions_count": 1,
                "total_pnl": pnl
            }
        }
    )
    
    # Record transaction
    transaction = {
        "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
        "user_id": user["user_id"],
        "action": "close_position",
        "position_id": position_id,
        "symbol": position["symbol"],
        "quantity": position["quantity"],
        "entry_price": position["entry_price"],
        "exit_price": current_price,
        "pnl": pnl,
        "pnl_percent": (pnl / position["invested"]) * 100,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.portfolio_transactions.insert_one(transaction)
    
    return {
        "message": "Position closed successfully",
        "pnl": round(pnl, 2),
        "pnl_percent": round((pnl / position["invested"]) * 100, 2),
        "new_cash": round(new_cash, 2)
    }

@router.post("/reset")
async def reset_portfolio(user: dict = Depends(require_auth)):
    """Reset portfolio to starting state"""
    db = await get_database()
    
    await db.user_portfolios.update_one(
        {"user_id": user["user_id"]},
        {
            "$set": {
                "cash": STARTING_CASH,
                "open_positions": [],
                "closed_positions_count": 0,
                "total_pnl": 0.0,
                "trades_count": 0,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {"message": "Portfolio reset successfully", "starting_cash": STARTING_CASH}

@router.get("/achievements")
async def get_achievements(user: dict = Depends(require_auth)):
    """Get all achievements"""
    db = await get_database()
    
    portfolio = await db.user_portfolios.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not portfolio:
        return {"achievements": [], "unlocked": [], "locked": list(ACHIEVEMENTS.keys())}
    
    unlocked = portfolio.get("achievements", [])
    locked = [key for key in ACHIEVEMENTS.keys() if key not in unlocked]
    
    achievements_list = []
    for key, data in ACHIEVEMENTS.items():
        achievements_list.append({
            "id": key,
            "name": data["name"],
            "description": data["description"],
            "unlocked": key in unlocked
        })
    
    return {
        "achievements": achievements_list,
        "unlocked_count": len(unlocked),
        "total_count": len(ACHIEVEMENTS)
    }
