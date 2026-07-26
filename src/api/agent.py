from fastapi import FastAPI, Request, APIRouter, UploadFile
from fastapi.responses import FileResponse, JSONResponse
import logging
from helpers.helpers import doc_to_markdown, generate_unique_filepath, save_file
from agents.graph import agents_wrapper
logger= logging.getLogger(__name__)


agent_router= APIRouter()


@agent_router.post("/agent_call")
async def agent_call(request:Request, jd:str, cv:UploadFile):
    
    file_path=generate_unique_filepath(cv.filename)
    await save_file(file_path,cv)
    print(f"file path: {file_path}")
    resume=doc_to_markdown(file_path)
    result= agents_wrapper(jd,resume)
    
    return FileResponse(
        path= result["output_file_path"],
        media_type="application/x-tex",
        filename="optimized.tex",
    )