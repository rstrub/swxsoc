from pathlib import Path

try:
    import tomllib
except ImportError:  # Python < 3.11
    import tomli as tomllib


def main():
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"

    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)

    # Show base dependencies (what gets installed with `pip install swxsoc`)
    print("=" * 60)
    print("BASE DEPENDENCIES (always installed):")
    print("=" * 60)
    for dep in data["project"]["dependencies"]:
        print("  -", dep)
    print()

    # Show optional dependencies
    print("=" * 60)
    print("OPTIONAL DEPENDENCIES:")
    print("=" * 60)
    print(list(data["project"]["optional-dependencies"].keys()))
    print()

    for name, deps in data["project"]["optional-dependencies"].items():
        print(f"{name}:")
        for dep in deps:
            print("  -", dep)
        print()

    # Check if current env is missing any base dependencies
    try:
        import importlib.metadata

        print("=" * 60)
        print("CHECKING CURRENT ENVIRONMENT:")
        print("=" * 60)

        installed = {pkg.name.lower() for pkg in importlib.metadata.distributions()}

        # Extract package names from dependencies (strip version specs)
        base_pkgs = []
        for dep in data["project"]["dependencies"]:
            pkg_name = (
                dep.split("[")[0]
                .split(">")[0]
                .split("<")[0]
                .split("=")[0]
                .split("!")[0]
                .strip()
            )
            base_pkgs.append(pkg_name)

        missing = [pkg for pkg in base_pkgs if pkg.lower() not in installed]

        if missing:
            print("⚠️  MISSING base dependencies in current environment:")
            for pkg in missing:
                print(f"   - {pkg}")
            print("\n   Run: pip install -e .")
        else:
            print("✅ All base dependencies installed")

    except ImportError:
        print("(skipping env check - importlib.metadata not available)")


if __name__ == "__main__":
    main()
