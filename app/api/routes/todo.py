from app.api.depends import SessionDep, CurrentUser
from fastapi import APIRouter, Body, HTTPException
from app.crud.TodoCRUD import TodoCRUD

router = APIRouter()


@router.get("/all", summary="查询当前用户所有的Todo")
def get_all_todos(session: SessionDep, currentUser: CurrentUser):
    crud = TodoCRUD(session)
    return crud.get_all(user_id=currentUser.id)


@router.post("/add", summary="创建一个新的Todo")
def add_todo(
    session: SessionDep, currentUser: CurrentUser, text: str = Body(embed=True)
):
    crud = TodoCRUD(session)
    crud.create(text, user_id=currentUser.id)
    return ""


@router.get("/pending", summary="查询当前用户未完成的Todo")
def get_pending_todos(session: SessionDep, currentUser: CurrentUser):
    crud = TodoCRUD(session)
    return crud.get_pending(user_id=currentUser.id)


@router.get("/completed", summary="查询当前用户已完成的Todo")
def get_completed_todos(session: SessionDep, currentUser: CurrentUser):
    crud = TodoCRUD(session)
    return crud.get_completed(user_id=currentUser.id)


@router.put("/complete", summary="将todo标记为已完成")
def mark_todo_complete(
    session: SessionDep, currentUser: CurrentUser, todo_id: str = Body(embed=True)
):
    crud = TodoCRUD(session)
    todo = crud.mark_complete(todo_id, user_id=currentUser.id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return ""


@router.delete("/delete", summary="删除Todo")
def delete_todo(
    session: SessionDep, currentUser: CurrentUser, todo_id: str = Body(embed=True)
):
    crud = TodoCRUD(session)
    result = crud.delete(todo_id, user_id=currentUser.id)
    if not result:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"deleted": True}
