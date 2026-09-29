"""Render every PlantUML diagram in diagrams/ into images/."""

import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

PLANTUML_VERSION = "1.2025.4"
PLANTUML_URL = (
    f"https://github.com/plantuml/plantuml/releases/download/"
    f"v{PLANTUML_VERSION}/plantuml-{PLANTUML_VERSION}.jar"
)


class PlantUmlJar:
    """Provides a local PlantUML jar, downloading it once on first use."""

    def __init__(self, cache_dir: Path) -> None:
        self._path = cache_dir / f"plantuml-{PLANTUML_VERSION}.jar"

    def path(self) -> Path:
        if not self._path.exists():
            self._download()
        return self._path

    def _download(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading PlantUML {PLANTUML_VERSION}...")
        urllib.request.urlretrieve(PLANTUML_URL, self._path)


class DiagramRenderer:
    """Renders .puml source files to PNG images."""

    def __init__(self, jar: PlantUmlJar, source_dir: Path, output_dir: Path) -> None:
        self._jar = jar
        self._source_dir = source_dir
        self._output_dir = output_dir

    def render_all(self) -> list[Path]:
        diagrams = sorted(self._source_dir.glob("*.puml"))
        if not diagrams:
            raise FileNotFoundError(f"No .puml files found in {self._source_dir}")
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._run(diagrams)
        return [self._output_dir / f"{d.stem}.png" for d in diagrams]

    def _run(self, diagrams: list[Path]) -> None:
        command = ["java", "-jar", str(self._jar.path()), "-tpng"]
        command += ["-o", str(self._output_dir.resolve())]
        command += [str(d) for d in diagrams]
        subprocess.run(command, check=True)


def main() -> None:
    if shutil.which("java") is None:
        sys.exit("Error: java is required to run PlantUML but was not found.")
    root = Path(__file__).parent
    jar = PlantUmlJar(Path.home() / ".cache" / "plantuml")
    renderer = DiagramRenderer(jar, root / "diagrams", root / "images")
    for image in renderer.render_all():
        print(f"Rendered {image.relative_to(root)}")


if __name__ == "__main__":
    main()
