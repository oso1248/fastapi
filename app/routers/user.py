from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import session
from .. import models, schemas, utils, oauth2
from .. database import get_db


router = APIRouter(prefix='/user', tags=['Users'])


@router.get('/{id}', response_model=schemas.UserOut)
def user_get(id: int, db: session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    data = db.query(models.User).filter(models.User.id == id).first()

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with id: {id} does not exist')

    return data


@router.post('', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def user_create(user: schemas.UserCreate, db: session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    does_exist = db.query(models.User).filter(
        models.User.email == user.email).first()

    if does_exist:
        raise HTTPException(status_code=status.HTTP_226_IM_USED,
                            detail=f'Email Taken')

    user.password = utils.hash(user.password)

    data = models.User(**user.dict())

    db.add(data)
    db.commit()
    db.refresh(data)

    return data
