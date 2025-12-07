from app.models.base_models.TodoBase import TodoBase
from sqlmodel import SQLModel
from app.models.base_models.SMSCodeRecordBase import SMSCodeRecordBase
from app.models.base_models.UserBase import UserBase
from typing import Optional, List
from sqlmodel import Field, Relationship
from uuid import UUID


# 用户表
class User(UserBase, table=True):
    todos: List["Todo"] = Relationship(back_populates="user")


# 短信发送记录
class SMSCodeRecord(SMSCodeRecordBase, table=True):
    pass


# 待办事项表
class Todo(TodoBase, table=True):
    user_id: UUID = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="todos")
