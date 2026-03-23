from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)
    content = Column(String)
    published = Column(Boolean, default=True)
#    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))


