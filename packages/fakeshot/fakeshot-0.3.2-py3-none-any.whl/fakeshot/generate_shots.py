from __future__ import annotations

from .logger import LOGGER
from .template import Template
from .generate_exr import generate_exr


def generate_shots(template: Template, output: str) -> None:
    """
    Generates dummy EXR files for all permutations defined by the template.

    This function creates directories and generates dummy EXR files for each combination
    of scene, shot, task, version, and frame as specified by the template.

    ```
    template = Template(...)
    generate_dummy_shots(template, './data')
    ```

    Args:
        template (Template): The template object containing shot parameters and file patterns.
        output (str): The root directory where the generated EXR files will be saved.

    Returns:
        None
    """
    LOGGER.info('Generating shots...')
    for shot in template.generate_shots_permutations():

        shot_path = shot.generate_path(template, output)
        shot_path.parent.mkdir(exist_ok=True, parents=True)

        LOGGER.debug('Generating: %s', shot_path)

        generate_exr(
            path=shot_path.as_posix(),
            label=shot_path.stem,
            width=template.width,
            height=template.height
        )

    LOGGER.info('EXR files generated.')
