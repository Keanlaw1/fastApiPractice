import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("activity")


async def log_request(request, call_next):
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        user_id = getattr(request.state, "user_id", "unidentified")
        logger.info(
            "user_id=%s method=%s path=%s status=%s",
            user_id,
            request.method,
            request.url.path,
            status_code,
        )
