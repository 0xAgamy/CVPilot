from fastapi import  Request, APIRouter, UploadFile, Form, File
from fastapi.responses import  JSONResponse
import logging
from helpers.helpers import doc_to_markdown, generate_unique_filepath, save_file
from agents.graph import agents_wrapper
logger= logging.getLogger(__name__)


agent_router= APIRouter()


@agent_router.post("/agent_call")
async def agent_call(request:Request, jd:str=Form(), cv:UploadFile=File()):
    
    file_path=generate_unique_filepath(cv.filename)
    await save_file(file_path,cv)
    print(f"file path: {file_path}")
    resume=doc_to_markdown(file_path)
    result= agents_wrapper(jd,resume)
    
    return JSONResponse(
        content={
            "score": result.get("score"),
            "optimization_suggestions": result.get("optimization_suggestion"),
            "optimized_cv": result["optimized_cv"],
            "download_url": f"{result.get("output_file_path")}",
        }
    )