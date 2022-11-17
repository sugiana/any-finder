from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    Float,
    DateTime,
    func,
    ForeignKey,
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


class TingkatWilayah(Base):
    __tablename__ = 'tingkat_wilayah'
    id = Column(Integer, primary_key=True)
    nama = Column(String(32), nullable=False, unique=True)


class JenisWilayah(Base):
    __tablename__ = 'jenis_wilayah'
    id = Column(Integer, primary_key=True)
    nama = Column(String(32), nullable=False, unique=True)
    tingkat_id = Column(
            Integer, ForeignKey(TingkatWilayah.id), nullable=False)


class Wilayah(Base):
    __tablename__ = 'wilayah'
    id = Column(Integer, primary_key=True)
    nama = Column(String(64), nullable=False, unique=True)
    key = Column(String(16), nullable=False, unique=True)
    wilayah_id = Column(Integer, ForeignKey('wilayah.id'))
    jenis_id = Column(Integer, ForeignKey(JenisWilayah.id))
    tingkat_id = Column(
            Integer, ForeignKey(TingkatWilayah.id), nullable=False)
    nama_lengkap = Column(String(256), nullable=False)


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
    shop_name = Column(Text, nullable=False)
    shop_url = Column(Text, nullable=False)
    city = Column(Text)
    hostname = Column(Text, nullable=False)
    wilayah_id = Column(Integer, ForeignKey(Wilayah.id))
    stock = Column(Integer)
