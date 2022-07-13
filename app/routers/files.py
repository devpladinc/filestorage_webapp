from typing import List
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from logging import raiseExceptions
from fastapi import status, Depends, APIRouter, UploadFile, HTTPException, Response
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


@router.delete("/delete-file/{file_id}")
async def delete_file_by_fileid(file_id:int, db: Session = Depends(database.get_db), authorized_user : int = Depends(oauth2.get_current_user)):
    # check existing bucket and connection 
    if database.check_bucket():
        # check if authorized user
        if authorized_user.user_id != None:
            user_id = authorized_user.user_id
            # check if file_id is owned by authorized_user
            # user_id from authorized_user vs. user_id from db
            file_owner = (db.query(models.Files).filter(models.Files.file_id==file_id).first()).user_id

            if user_id == file_owner:
                # proceed with deletion; retrive filename
                file_name = (db.query(models.Files).filter(models.Files.file_id==file_id).first()).file_name
                # delete from gcp
                delete_status = database.delete_file(file_name)
                # delete from db
                file = db.query(models.Files).filter(models.Files.file_id==file_id)
                file.delete(synchronize_session=False)
                db.commit()

                if delete_status:
                    return Response(status_code=status.HTTP_204_NO_CONTENT)

            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Unable to delete file. Unauthorized access.")


@router.get("/download-file/{file_id}")
async def download_file_by_fileid(file_id:int, db: Session = Depends(database.get_db), authorized_user : int = Depends(oauth2.get_current_user)):
    # check existing bucket and connection 
    if database.check_bucket():
        if authorized_user.user_id != None:
            user_id = authorized_user.user_id
            file_owner = (db.query(models.Files).filter(models.Files.file_id==file_id).first()).user_id

            if user_id == file_owner:
                # proceed with download; retrive filename
                file_name = (db.query(models.Files).filter(models.Files.file_id==file_id).first()).file_name
                download_status = database.download_file(file_name)
                
                if download_status:
                    return Response(status_code=status.HTTP_204_NO_CONTENT)

            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Unable to delete file. Unauthorized access.")