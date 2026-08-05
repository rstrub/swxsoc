import tomllib
from pprint import pprint

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)
print(data["project"]["optional-dependencies"].keys())


with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

for name, deps in data["project"]["optional-dependencies"].items():
    print(f"{name}:")
    for dep in deps:
        print("  -", dep)
    print()

