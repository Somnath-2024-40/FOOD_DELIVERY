from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column, DeclarativeBaseNoMeta
from sqlalchemy import Column, DateTime, func


class Base(DeclarativeBase):   
    pass


class Timestamp:
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  
        onupdate=func.now(),         
        nullable=False,
    )