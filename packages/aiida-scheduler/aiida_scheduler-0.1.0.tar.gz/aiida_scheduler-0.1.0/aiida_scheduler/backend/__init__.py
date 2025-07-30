import pathlib
from .scheduler import router as scheduler_router

__version__ = "0.1.1"

# static_dir points to plugin1/static
THIS_DIR = pathlib.Path(__file__).parent
static_dir = str(THIS_DIR / "static")

plugin = {
    "routers": {
        "scheduler": scheduler_router,
    },
    "name": "Scheduler",
    "static_dirs": {"scheduler": static_dir},
}
