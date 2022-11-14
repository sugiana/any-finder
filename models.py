from sqlalchemy import (
    Column,
    Integer,
    Text,
    Float,
    DateTime,
    func,
    )
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Common:
    def to_dict(self):
        values = {}
        for column in self.__table__.columns:
            values[column.name] = getattr(self, column.name)
        return values

    def from_dict(self, values):
        for column in self.__table__.columns:
            if column.name in values:
                setattr(self, column.name, values[column.name])


class Product(Common, Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    created = Column(
            DateTime(timezone=True), nullable=False, server_default=func.now())
    updated = Column(
            DateTime(timezone=True), nullable=False, server_default=func.now())
    url = Column(Text, nullable=False, unique=True)
    title = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    image = Column(Text, nullable=False)
