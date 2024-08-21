import datetime

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from orm_manager.db_session import SqlAlchemyBase


class Person:
    name: Mapped[str]
    surname: Mapped[str]
    middle_name: Mapped[str]
    phone_number: Mapped[str]


class User(Person, SqlAlchemyBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_type: Mapped[str]

    meetings: Mapped[list["Meeting"]] = relationship(
        back_populates="user",
        uselist=True,
        lazy="subquery",
    )


class Courier(Person, SqlAlchemyBase):
    __tablename__ = "couriers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    meetings: Mapped[list["Meeting"]] = relationship(
        back_populates="courier", uselist=True, lazy="subquery"
    )


class AdditionalUser(Person, SqlAlchemyBase):
    __tablename__ = "additional_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    role: Mapped[str]
    passport_data: Mapped[str]
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))

    meeting: Mapped["Meeting"] = relationship(
        back_populates="additional_users", lazy="subquery"
    )


class Meeting(SqlAlchemyBase):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    location: Mapped[str]

    start_datetime: Mapped[datetime.datetime]
    end_datetime: Mapped[datetime.datetime]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    courier_id = mapped_column(ForeignKey("couriers.id"))

    user: Mapped["User"] = relationship(
        back_populates="meetings",
        uselist=False,
        lazy="subquery",
    )
    courier: Mapped["Courier"] = relationship(
        back_populates="meetings",
        uselist=False,
        lazy="subquery",
    )

    additional_users: Mapped[list["AdditionalUser"]] = relationship(
        back_populates="meeting",
        uselist=True,
        lazy="subquery",
        cascade="all, delete",
    )
    products: Mapped[list["Product"]] = relationship(
        back_populates="meetings",
        secondary="meetings_to_products",
        uselist=True,
        lazy="subquery",
    )


class Product(SqlAlchemyBase):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str]
    time: Mapped[int]

    documents: Mapped[list["Document"]] = relationship(
        back_populates="products",
        secondary="documents_to_products",
        uselist=True,
        lazy="subquery",
    )
    meetings: Mapped[list["Meeting"]] = relationship(
        back_populates="products",
        secondary="meetings_to_products",
        uselist=True,
        lazy="subquery",
    )


class Document(SqlAlchemyBase):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str]
    for_LLC: Mapped[bool]

    products: Mapped[list["Product"]] = relationship(
        back_populates="documents",
        secondary="documents_to_products",
        uselist=True,
        lazy="subquery",
    )


class MeetingToProduct(SqlAlchemyBase):
    __tablename__ = "meetings_to_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))


class DocumentToProduct(SqlAlchemyBase):
    __tablename__ = "documents_to_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
