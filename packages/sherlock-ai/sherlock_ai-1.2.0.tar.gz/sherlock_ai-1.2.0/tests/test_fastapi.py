from fastapi import FastAPI, Request
from sherlock_ai import get_logger, set_request_id
import uuid
from sherlock_ai import log_performance, monitor_memory, monitor_resources

logger = get_logger("ApiLogger")

def create_app():
    app = FastAPI()

    @log_performance
    @monitor_memory
    @monitor_resources
    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        # request_id = str(uuid.uuid4())
        request_id = set_request_id()
        request.state.request_id = request_id
        logger.info(f"Request started")
        response = await call_next(request)
        logger.info(f"Request completed")
        response.headers["X-Request-ID"] = request_id
        return response

    @app.get("/health")
    @log_performance
    @monitor_memory
    @monitor_resources
    def health_check():
        try:
            logger.info("Health check")
            print(1/0)
            return {"message": "OK"}
        except Exception as e:
            logger.error(f"Error in health check: {e}")
        
    return app

app = create_app()
