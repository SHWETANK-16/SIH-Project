import logging,time
from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.config.settings import get_settings
from app.config.logging import configure_logging
from app.exceptions.handlers import register_exception_handlers

settings=get_settings(); configure_logging(settings.log_level); log=logging.getLogger("api")
app=FastAPI(title=settings.app_name,description="Explainable financial network intelligence baseline. All findings and data are synthetic demonstrations.",version="0.1.0",docs_url="/docs",redoc_url="/redoc")
app.add_middleware(CORSMiddleware,allow_origins=[settings.frontend_url],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.middleware("http")
async def request_log(request:Request,call_next):
    started=time.perf_counter(); response=await call_next(request); log.info("%s %s %s %.1fms",request.method,request.url.path,response.status_code,(time.perf_counter()-started)*1000); return response
@app.get("/health",tags=["Health"])
def health(): return {"status":"healthy","service":settings.app_name,"version":"0.1.0","data":"SYNTHETIC"}
app.include_router(api_router,prefix=settings.api_prefix)
register_exception_handlers(app)
