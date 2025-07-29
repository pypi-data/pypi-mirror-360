# json_api_builder/__init__.py
from .builder import AppBuilder
from .db_generator import generate_db_from_json_file

__all__ = ["AppBuilder", "generate_db_from_json_file"]
