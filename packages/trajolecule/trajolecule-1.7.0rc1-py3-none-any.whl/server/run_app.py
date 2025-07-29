from easytrajh5.fs import load_yaml_dict
from path import Path

from server.app import make_app, init_logging

init_logging()
config = load_yaml_dict(Path(__file__).parent / "app.yaml")
app = make_app(config)
