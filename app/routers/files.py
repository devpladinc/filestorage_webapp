from typing import List
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from logging import raiseExceptions
from fastapi import status, Depends, APIRouter, UploadFile, HTTPException
from .. import database


router = APIRouter(
    tags = ["Files"],
    prefix = "/files"
)

@router.get("/", response_model=List[schemas.Files])
async def get_all_files(db: Session = Depends(database.get_db)):

    files = db.query(models.Files).all()
    return files


@router.get("/{user_id}", response_model=List[schemas.FileUploadOut])
async def get_files_by_userid(user_id: int, db: Session = Depends(database.get_db)):
    
    files = db.query(models.Files).filter(models.Files.user_id==user_id).all()
    print(files)
    if len(files) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No files under {user_id} found")

    return files


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
            
            # save file path to db
            new_file = models.Files(user_id=user_id, file_name=file.filename, file_path=blob_link)
            db.add(new_file)
            db.commit()
            db.refresh(new_file)

            return new_file

        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Unable to upload file. Unauthorized access.")
    else:
        return {'status': 403, 'description': 'Bucket not found'}