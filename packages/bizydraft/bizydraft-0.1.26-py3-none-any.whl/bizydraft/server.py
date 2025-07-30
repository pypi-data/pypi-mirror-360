import os

from loguru import logger

try:
    from server import PromptServer
except ImportError:
    logger.error(
        "Failed to import ComfyUI server modules, ensure PYTHONPATH is set correctly. (export PYTHONPATH=$PYTHONPATH:/path/to/ComfyUI)"
    )
    exit(1)


from .resp import OKResponse, ErrResponse

_API_PREFIX = "bizyair"
_SERVER_MODE_HC_FLAG = True

BIZYAIR_MAGIC_STRING = os.getenv("BIZYAIR_MAGIC_STRING", "QtDtsxAc8JI1bTb7")

if BIZYAIR_MAGIC_STRING == "QtDtsxAc8JI1bTb7":
    logger.warning(
        "BIZYAIR_MAGIC_STRING is not set, using default value. This is insecure and should be changed in production!"
    )


class BizyDraftServer:
    def __init__(self):
        BizyDraftServer.instance = self
        self.prompt_server = PromptServer.instance
        self.setup_routes()

    def setup_routes(self):
        @self.prompt_server.routes.get(f"/{_API_PREFIX}/are_you_alive")
        async def are_you_alive(request):
            if _SERVER_MODE_HC_FLAG:
                return OKResponse()
            return ErrResponse(500)

        @self.prompt_server.routes.post(
            f"/{_API_PREFIX}/are_you_alive_{BIZYAIR_MAGIC_STRING}"
        )
        async def toggle_are_you_alive(request):
            global _SERVER_MODE_HC_FLAG
            _SERVER_MODE_HC_FLAG = not _SERVER_MODE_HC_FLAG
            return OKResponse()
