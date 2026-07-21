import tempfile
import os
from scancode.api import get_licenses

def match_license_text(text: str):
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(text)
        tmp_path = tmp.name

    try:
        results = get_licenses(tmp_path)
        return results
    finally:
        os.remove(tmp_path)

dependency_files = {
    # Python
    "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg",
    "pipfile", "pipfile.lock", "poetry.lock", "environment.yml",
    # JavaScript / Node
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    # Ruby
    "gemfile", "gemfile.lock",
    # Rust
    "cargo.toml", "cargo.lock",
    # Go
    "go.mod", "go.sum",
    # Java / JVM
    "pom.xml", "build.gradle", "build.gradle.kts", "gradle.lockfile",
    # PHP
    "composer.json", "composer.lock",
    # .NET
    "packages.config", "*.csproj",
    # C/C++
    "conanfile.txt", "conanfile.py", "vcpkg.json",
    # Other
    "mix.exs", "mix.lock",  # Elixir
    "dependencies.yaml",    # Generic
}