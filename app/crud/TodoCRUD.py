from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from app.models.table import Todo


class TodoCRUD:
    """Todo 数据库操作工具类"""

    def __init__(self, session: Session):
        self.session = session

    def get_all(self, user_id: UUID) -> List[Todo]:
        """获取当前用户所有未删除的Todo"""
        stmt = select(Todo).where(
            (Todo.is_deleted == False) & (Todo.user_id == user_id)
        )
        return self.session.exec(stmt).all()

    def get_by_id(self, todo_id: str, user_id: UUID) -> Optional[Todo]:
        """根据ID获取单个Todo，并验证所有权"""
        todo = self.session.get(Todo, todo_id)
        # 验证Todo存在且属于当前用户
        if todo is None or todo.user_id != user_id:
            return None
        return todo

    def create(self, text: str, user_id: UUID) -> Todo:
        """创建新的Todo"""
        new_todo = Todo(text=text, user_id=user_id)
        self.session.add(new_todo)
        self.session.commit()
        return new_todo

    def get_pending(self, user_id: UUID) -> List[Todo]:
        """获取当前用户未完成的Todo"""
        stmt = select(Todo).where(
            (Todo.is_deleted == False)
            & (Todo.completed == False)
            & (Todo.user_id == user_id)
        )
        return self.session.exec(stmt).all()

    def get_completed(self, user_id: UUID) -> List[Todo]:
        """获取当前用户已完成的Todo"""
        stmt = select(Todo).where(
            (Todo.is_deleted == False)
            & (Todo.completed == True)
            & (Todo.user_id == user_id)
        )
        return self.session.exec(stmt).all()

    def mark_complete(self, todo_id: str, user_id: UUID) -> Optional[Todo]:
        """将Todo标记为已完成，需验证所有权"""
        todo = self.get_by_id(todo_id, user_id)
        if todo is None:
            return None
        todo.completed = True
        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def delete(self, todo_id: str, user_id: UUID) -> bool:
        """软删除Todo，需验证所有权"""
        todo = self.get_by_id(todo_id, user_id)
        if todo is None:
            return False
        todo.is_deleted = True
        self.session.add(todo)
        self.session.commit()
        return True
