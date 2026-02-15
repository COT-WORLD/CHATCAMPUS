import logging
import traceback

logger = logging.getLogger(__name__)

class Immediate500Logger:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            if response.status_code >= 500:
                logger.critical(f"500 response for {request.path}")
            return response
        except Exception as e:
            logger.critical(f"EXCEPTION in {request.path}: {str(e)}\n{traceback.format_exc()}")
            raise