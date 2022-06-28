from sys import prefix
from typing import List
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from logging import raiseExceptions
from fastapi import status, Response, Depends, APIRouter, UploadFile
from ..database import get_db
from ..utils import util


router = APIRouter(
    tags = ["Files"],
    prefix = "/files"
)

@router.get("/", response_model=List[schemas.Files])
async def get_all_files(db: Session = Depends(get_db)):

    files_db = db.query(models.Files).all()
    print("files:", files_db)
    return files_db


@router.post("/upload_file/", response_model=schemas.FileOut)
async def create_upload_file(file: UploadFile):

    return {
        "file_name" : file.filename,
        "file_type" : file.content_type
        }