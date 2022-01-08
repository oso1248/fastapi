from fastapi import Response, status, HTTPException, Depends, APIRouter
from typing import List, Optional
import sqlalchemy
from sqlalchemy.orm import session
from sqlalchemy import func, text
from .. import models, schemas, oauth2
from .. database import get_db, engine, SessionSQL
from sqlalchemy.sql import text


router = APIRouter(prefix='/post', tags=['Posts'])


# @router.get('/sql')
# def get_post_all():
#     sql = SessionSQL()
#     result = sql.execute(text('SELECT * FROM post'))
#     print(result)
#     # with engine.connect() as conn:
#     #     rs = conn.execute('SELECT * FROM post')
#     #     for row in rs:
#     #         print(row)

#     return {'message': 'hello'}


@router.post('', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    data = models.Post(user_id=current_user.id, **post.dict())
    db.add(data)
    db.commit()
    db.refresh(data)

    return data


@router.put('/{id}', response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate, db: session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    data_query = db.query(models.Post).filter(models.Post.id == id)

    data = data_query.first()

    if data == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id: {id} not found.')

    if data.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not authorized to perform requested action')

    data_query.update(post.dict(), synchronize_session=False)
    db.commit()

    return data_query.first()


@router.get('', response_model=List[schemas.PostOut])
def get_post(db: session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
             limit: int = 10, skip: int = 0, search_title: Optional[str] = '', user_id: Optional[int] = None):

    if user_id:
        data_query = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(
            models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
                models.Post.id).filter(
                    models.Post.title.contains(search_title), models.Post.user_id == user_id).order_by(
                        models.Post.created_at.desc()).limit(limit).offset(skip)
    else:
        data_query = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(
            models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
                models.Post.id).filter(
                    models.Post.title.contains(search_title), models.Post.published == True).order_by(
                        models.Post.created_at.desc()).limit(limit).offset(skip)

    data = data_query.all()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail='no posts exist')
    print(data)
    return data


@router.get('/{id}', response_model=schemas.PostOut)
def get_post(id: int, db: session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    data = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.id == id).first()

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id: {id} not found')

    return data


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    data_query = db.query(models.Post).filter(models.Post.id == id)

    data = data_query.first()

    if data == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id: {id} not found.')

    if data.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='not authorized to perform requested action')

    data_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
