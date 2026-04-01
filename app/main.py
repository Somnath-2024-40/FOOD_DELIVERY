
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.api import api_router
from core.config import settings
from db.base import Base
from db.session import engine, sessionlocal
from models.user import UserRole                             
from schemas.user import UserCreate                          
from services.user import _get_user_by_email, create_user    


# ── Startup helpers ───────────────────────────────────────────────────────────

async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# async def create_first_superuser() -> None:
#     async with sessionlocal() as db:                          
#         existing = await _get_user_by_email(db, settings.FIRST_SUPERUSER_EMAIL)
#         if not existing:
#             await create_user(                                 
#                 db,
#                 UserCreate(
#                     email=settings.FIRST_SUPERUSER_EMAIL.strip(),
#                     password=settings.FIRST_SUPERUSER_PASSWORD.strip(),
#                     full_name="System Admin",
#                     role=UserRole.ADMIN,
#                 ),
#             )
#             print("First superuser created.")


async def create_first_superuser() -> None:
    async with sessionlocal() as db:
        email = settings.FIRST_SUPERUSER_EMAIL.strip()
        existing = await _get_user_by_email(db, email)
        
        if not existing:
            # Create the user first
            new_user = await create_user(
                db,
                UserCreate(
                    email=email,
                    password=settings.FIRST_SUPERUSER_PASSWORD.strip(),
                    full_name="System Admin",
                )
            )
            
            new_user.role = UserRole.ADMIN
            await db.commit()
            print(f"First superuser {email} and  and password {settings.FIRST_SUPERUSER_PASSWORD} created and promoted to ADMIN.")
        else:
           
            if existing.role != UserRole.ADMIN:
                existing.role = UserRole.ADMIN
                await db.commit()
                print(f"Superuser {email} role corrected to ADMIN.")


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    await create_first_superuser()
    yield


# ── App ───────────────────────────────────────────────────────────────────────

app= FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,                                # ✅ correct attribute name
    version="1.0.0",
    description="A restaurant management system API built with FastAPI and SQLAlchemy.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")