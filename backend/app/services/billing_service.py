"""Billing service for handling user credits and transactions."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.user import User
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)

class BillingService:
    async def add_credits(
        self, db: AsyncSession, user_id: int, amount: float, description: str, entity_type: str = None, entity_id: int = None
    ) -> float:
        """Add credits to a user's balance."""
        if amount <= 0:
            raise ValueError("Amount to add must be positive")
            
        user = await db.get(User, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
            
        user.credits += amount
        
        tx = Transaction(
            user_id=user_id,
            amount=amount,
            description=description,
            related_entity_type=entity_type,
            related_entity_id=entity_id
        )
        db.add(tx)
        await db.flush()
        
        logger.info(f"Added ${amount} credits to user {user_id}. New balance: ${user.credits}")
        return user.credits

    async def deduct_credits(
        self, db: AsyncSession, user_id: int, amount: float, description: str, entity_type: str = None, entity_id: int = None
    ) -> float:
        """Deduct credits from user. Raises 402 if insufficient balance."""
        if amount <= 0:
            raise ValueError("Amount to deduct must be positive")
            
        user = await db.get(User, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
            
        if user.credits < amount:
            logger.warning(f"User {user_id} has insufficient credits (${user.credits}) for $${amount} deduction: {description}")
            raise HTTPException(
                status_code=402, 
                detail=f"Saldo insuficiente. Requieres ${amount:.2f} créditos pero tienes ${user.credits:.2f}."
            )
            
        user.credits -= amount
        
        tx = Transaction(
            user_id=user_id,
            amount=-amount, # Negative for deduction
            description=description,
            related_entity_type=entity_type,
            related_entity_id=entity_id
        )
        db.add(tx)
        await db.flush()
        
        logger.info(f"Deducted ${amount} from user {user_id}. Remaining balance: ${user.credits}")
        return user.credits
        
billing_service = BillingService()
