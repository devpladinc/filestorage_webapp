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
@router.post("/upload-file", status_code=status.HTTP_201_CREATED, response_model=schemas.FileUploadOut)
async def create_upload_file(file: UploadFile, db: Session = Depends(database.get_db), authorized_user : int = Depends(oauth2.get_current_user)):
    # check existing bucket and connection 
    if database.check_bucket():
        # check user access to upload
        if authorized_user.user_id != None:
            user_id = authorized_user.user_id
            # upload file
            blob_link = database.upload_file(file.filename)
            print("blob link:", blob_link)
            
            new_file = models.Files(user_id=user_id, file_name=file.filename, file_path=blob_link)
            db.add(new_file)
            db.commit()
            db.refresh(new_file)

            return new_file

        else:
            raiseExceptions(status_code=status.HTTP_403_FORBIDDEN, detail=f"Unable to upload file. Unauthorized access.")
    else:
        return {'status': 403, 'description': 'Bucket not found'}