from functools import lru_cache
import pathlib
import tomllib


@lru_cache(maxsize=1)
def get_package_info():
    try:
        current_dir = pathlib.Path(__file__).parent

        pyproject_path = current_dir / "pyproject.toml"

        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomllib.load(f)
                return (
                    pyproject_data.get("project", {}).get("name", "ac-mcp-client"),
                    pyproject_data.get("project", {}).get("version", "0.1.0"),
                )
        return "ac-mcp-client", "0.1.0"
    except Exception:
        return "ac-mcp-client", "0.1.0"
