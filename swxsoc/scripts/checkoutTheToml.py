try:
    import tomllib
except ImportError:  # Python < 3.11
    import tomli as tomllib

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

