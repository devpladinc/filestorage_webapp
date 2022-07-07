from typing import List
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from logging import raiseExceptions
from fastapi import status, Response, Depends, APIRouter, File, UploadFile
from .. import database
from ..utils import util


router = APIRouter(
    tags = ["Files"],
    prefix = "/files"
)

@router.get("/", response_model=List[schemas.Files])
async def get_all_files(db: Session = Depends(database.get_db)):

    files_db = db.query(models.Files).all()
    return files_db

# form-data key should match parameter ('file') for testing
@router.post("/upload-file")
async def create_upload_file():
    
    if database.check_bucket():
        # check user access to upload
        pass