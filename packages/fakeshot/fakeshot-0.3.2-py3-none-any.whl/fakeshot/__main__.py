from __future__ import annotations

import sys
import json
import logging
import argparse
from dataclasses import asdict

from .logger import LOGGER, CONSOLE_LOGGER
from .template import Template
from .generate_csv import generate_csv
from .generate_shots import generate_shots


def main():
    parser = argparse.ArgumentParser(
        description='Generate dummy EXR files following VFX naming conventions.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        usage="""
Examples:
  fakeshot --out ./renders
    Generate using default template to ./renders directory

  fakeshot --show myfilm --scene 010,020 --shot 0010,0020 --task comp,anim
    Generate shots for 'myfilm' with multiple scenes, shots, and tasks

  fakeshot --end_frame 1024 --width 1920 --height 1080
    Generate HD frames from 1001 to 1023

  fakeshot --template custom.json --out /path/to/output
    Use custom template file

  fakeshot --sample-template > my_template.json
    Generate a sample template file
        """.strip()
    )

    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    parser.add_argument('--out', help='Output directory for EXR files. (default: ./out)')
    parser.add_argument('--template', help='Specify a different template.json')
    parser.add_argument('--sample-template', action='store_true', help='Output a sample template')
    parser.add_argument('--csv', action='store_true',
                        help='Export as csv rather than creating the shots.')

    template = Template()

    parser.add_argument(
        '--show', default=template.show,
        help="Project/show name (e.g., 'prj', 'film_abc')"
    )
    parser.add_argument(
        '--scene', default=template.scene,
        help="Scene identifier(s), comma-separated (e.g., '001', '001,002,003')"
    )
    parser.add_argument(
        '--shot', default=template.shot,
        help="Shot identifier(s), comma-separated (e.g., '0010', '0010,0020,0030')"
    )
    parser.add_argument(
        '--task', default=template.task,
        help="Task type(s), comma-separated (e.g., 'comp', 'comp,anim,lighting')"
    )
    parser.add_argument(
        '--version', default=template.version,
        help="Version identifier(s), comma-separated (e.g., 'v001', 'v001,v002')"
    )
    parser.add_argument(
        '--start_frame', type=int, default=template.start_frame,
        help='Starting frame number (inclusive)'
    )
    parser.add_argument(
        '--end_frame', type=int, default=template.end_frame,
        help='Ending frame number (exclusive)'
    )
    parser.add_argument(
        '--width', type=int, default=template.width,
        help='Image width in pixels'
    )
    parser.add_argument(
        '--height', type=int, default=template.height,
        help='Image height in pixels'
    )
    parser.add_argument(
        '--path-pattern', default=template.path_pattern,
        help='Directory structure pattern tokens'
    )
    parser.add_argument(
        '--file-pattern', default=template.file_pattern,
        help='Filename pattern tokens'
    )

    args = parser.parse_args()

    if args.verbose:
        CONSOLE_LOGGER.setLevel(logging.DEBUG)

    if args.sample_template:
        print(json.dumps(asdict(template), indent=4))
        sys.exit(0)

    # Apply CLI arguments to template
    for attr, value in args._get_kwargs():
        if hasattr(template, attr):
            setattr(template, attr, value)

    if args.template:
        LOGGER.info('Using user template: %s', args.template)
        with open(args.template) as f:
            template.update(json.load(f))

    if args.csv:
        generate_csv(template, args.out)
        sys.exit(0)

    generate_shots(template, args.out or './out')

    sys.exit(0)


if __name__ == '__main__':
    main()
