from sqlalchemy import Column, String, Integer, Float, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import relationship
from svc_order_zxw.apis.schemas_payments import OrderStatus, PaymentMethod
from svc_order_zxw.db.get_db import Base


class Application(Base):
    """应用表"""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    products = relationship("Product", back_populates="app")


class Product(Base):
    """产品表"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    app_id = Column(Integer, ForeignKey("applications.id"))
    app = relationship("Application", back_populates="products")
    orders = relationship("Order", back_populates="product")


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user_id = Column(String, index=True)
    total_price = Column(Float, nullable=False, comment="订单总金额")
    quantity = Column(Integer, nullable=False, default=1, comment="购买数量")

    # 外键:商品
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="orders")
    # 外键:优惠卷 - 二期计划
    # user_coupon_id = Column(Integer, ForeignKey('user_coupons.user_coupon_id'))
    # user_coupon = relationship("UserCoupon", back_populates="order")
    # 外键:支付
    payment = relationship("Payment", back_populates="order", uselist=False)


class Payment(Base):
    """支付记录表"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    payment_price = Column(Float, nullable=False, comment="支付金额")
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)

    callback_url = Column(String, nullable=True)
    payment_url = Column(String, nullable=True)

    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    order = relationship("Order", back_populates="payment")
