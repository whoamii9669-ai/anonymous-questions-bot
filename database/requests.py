from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from database.models import Base, User

import random
import string

engine = create_async_engine("sqlite+aiosqlite:///db.db", echo=False)
session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def generator():
    upper = random.choice(string.ascii_uppercase)
    lowers = random.choices(string.ascii_lowercase, k=3)
    digits = random.choices(string.digits, k=2)

    chars = [upper, *lowers, *digits]
    random.shuffle(chars)
    return ''.join(chars)

async def create():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def new(id:int):
    async with session() as db:
        user = await db.get(User, id)
        
        if user:
            return user.link
        while True:
            link = generator()
            
            _ = await db.scalar(select(User).where(User.link==link))
            
            if not _:
                db.add(User(id=id, link=link))
                await db.commit()
                return link
                

async def getUser(id:int):
    async with session() as db:
        user = await db.get(User,id)
        return user

async def getUserByLink(link:str):
    async with session() as db:
        user = await db.scalar(select(User).where(User.link==link))
        return user