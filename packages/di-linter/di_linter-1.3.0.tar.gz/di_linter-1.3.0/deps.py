from pathlib import Path
from pprint import pprint

from di_linter.graph import build_dependency_graph

project_path = Path("example")
graph = build_dependency_graph(project_path)

pprint(graph)
