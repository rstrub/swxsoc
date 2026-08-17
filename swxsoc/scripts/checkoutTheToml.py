from pathlib import Path

try:
    import tomllib
except ImportError:  # Python < 3.11
    import tomli as tomllib


def main():
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"

    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)

    print(data["project"]["optional-dependencies"].keys())

    for name, deps in data["project"]["optional-dependencies"].items():
        print(f"{name}:")
        for dep in deps:
            print("  -", dep)
        print()


if __name__ == "__main__":
    main()

