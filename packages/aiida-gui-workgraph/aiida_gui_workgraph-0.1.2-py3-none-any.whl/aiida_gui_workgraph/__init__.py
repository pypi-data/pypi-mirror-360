import pathlib
from .workgraph import router as workgraph_router

__version__ = "0.1.2"

# static_dir points to plugin1/static
THIS_DIR = pathlib.Path(__file__).parent
static_dir = str(THIS_DIR / "static")

plugin = {
    "routers": {
        "workgraph": workgraph_router,
    },
    "name": "WorkGraph",
    "static_dirs": {"workgraph": static_dir},
}
