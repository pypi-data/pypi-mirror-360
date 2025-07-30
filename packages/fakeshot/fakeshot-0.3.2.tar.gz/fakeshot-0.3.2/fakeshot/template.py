from __future__ import annotations

from typing import Any, Iterator, Generator
from pathlib import Path
from itertools import product
from dataclasses import asdict, dataclass


def split_n_strip(s: str, delimiter: str = ',') -> list[str]:
    """Split by delimiter and strip white space."""
    return [s.strip() for s in s.split(delimiter)]


@dataclass(frozen=True)
class Shot:
    show: str
    scene: str
    shot: str
    task: str
    version: str
    frame: int

    def generate_path(self, template: Template, output: str) -> Path:
        data = asdict(self)
        data['frame'] = f'{self.frame:04d}'

        path = f'{template.path_pattern}/{template.file_pattern}.exr'
        return Path(output, path.format(**data))


@dataclass(kw_only=True)
class Template:
    show: str = 'prj'
    scene: str = '001,002'
    shot: str = '0010,0020'
    task: str = 'comp,anim'
    version: str = 'v001'
    start_frame: int = 1001
    end_frame: int = 1010
    width: int = 512
    height: int = 512
    path_pattern: str = '{show}/{scene}/{shot}/{task}/{version}'
    file_pattern: str = '{show}_{scene}_{shot}_{task}_{version}.{frame}'

    def _get_permutations(self) -> Iterator[Any]:
        """
        Generates all possible permutations of scene, shot, task, version, and frame range.

        Yields:
            Iterator[Any]: An iterator over tuples containing all combinations
            of the split values of show, scene, shot, task, version, and
            each frame in the specified range.
        """
        return product(
            [self.show],
            self.get_scenes(),
            self.get_shots(),
            self.get_tasks(),
            self.get_versions(),
            range(self.start_frame, self.end_frame),
        )

    def get_scenes(self) -> list[str]:
        return split_n_strip(self.scene)

    def get_shots(self) -> list[str]:
        return split_n_strip(self.shot)

    def get_tasks(self) -> list[str]:
        return split_n_strip(self.task)

    def get_versions(self) -> list[str]:
        return split_n_strip(self.version)

    def generate_shots_permutations(self) -> Generator[Shot, Any, None]:
        """Returns a generator of Shot objects based on the current template data."""
        for _shot_permutation in self._get_permutations():
            yield Shot(*_shot_permutation)

    def update(self, user_template: dict[str, Any]):
        """Update current instance with dictionary data."""
        for k, v in user_template.items():
            setattr(self, k, v)
