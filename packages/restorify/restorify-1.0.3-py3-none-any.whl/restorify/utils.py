import json
from pathlib import Path
import re


_pattern = re.compile(r'(?<!^)(?=[A-Z])')
def camel_to_snake(camel: str) -> str:
   return _pattern.sub('_', camel).lower()

def snake_to_camel(snake: str) -> str:
    return "".join(w.capitalize() for w in snake.split('_'))

class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)
    
def write_json(what: dict, where: Path, how: str = "w"):
   with open(where, how, encoding="utf-8") as f:
      json.dump(what, f, ensure_ascii=False, indent=4, cls=CustomJsonEncoder)

def read_json(where_from: Path) -> str:
   with open(where_from, "r", encoding="utf-8") as f:
      return json.loads(f.read())

def read_text(where_from: Path):
   with open(where_from, "r", encoding="utf-8") as f:
      return f.read()
