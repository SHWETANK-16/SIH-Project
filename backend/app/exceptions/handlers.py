from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class NotFoundError(Exception):
    def __init__(self, code: str, message: str): self.code, self.message = code, message

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(NotFoundError)
    async def not_found(_: Request, exc: NotFoundError):
        return JSONResponse(status_code=404,content={"error":{"code":exc.code,"message":exc.message}})
    @app.exception_handler(Exception)
    async def unexpected(_: Request, exc: Exception):
        app.logger.exception("Unhandled application error", exc_info=exc) if hasattr(app,"logger") else None
        return JSONResponse(status_code=500,content={"error":{"code":"INTERNAL_ERROR","message":"The request could not be completed."}})
