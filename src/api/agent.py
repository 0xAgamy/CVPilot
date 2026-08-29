from fastapi import  Request, APIRouter, UploadFile, Form, File
from fastapi.responses import  JSONResponse
import logging
from src.helpers.helpers import doc_to_markdown, generate_unique_filepath, save_file
from src.agents.graph import agents_wrapper
logger= logging.getLogger(__name__)


agent_router= APIRouter()


@agent_router.post("/agent_call")
async def agent_call(request:Request, jd:str=Form(), cv:UploadFile=File()):
    graph= request.app.state.depends.graph
    
    file_path=generate_unique_filepath(cv.filename)
    await save_file(file_path,cv)
    resume=doc_to_markdown(file_path)
 
    result= agents_wrapper(graph,jd, resume)
    critique_history=result.get("critique_history",[])

    critique_hist= " ".join(critique_history)
    return JSONResponse(
        content={
            "score": result.get("score"),
            "optimization_summary": result.get("optimization_summary"),
            "critique_history":critique_hist,
            "optimized_cv": result["optimized_cv"],
            
        }
    )