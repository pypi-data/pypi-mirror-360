# fakeshot

A simple tool that generates dummy EXR files for VFX projects. Useful when you need placeholder renders that follow proper naming conventions.

## What it does

Creates fake EXR image files organized in the typical VFX directory structure:

```
project/scene/shot/task/version/project_scene_shot_task_version.frame.exr
```

Each EXR has the filename written in the center so you can tell what's what.

## Install

```bash
pip install fakeshot
```

Or even better
```bash
pipx install fakeshot
```

## Basic usage

Just run it and it'll create some sample files in an `./out` folder:

```bash
fakeshot
```

## Customize it

You can change most things with command line options:

```bash
fakeshot \
  --show "myproject" \
  --scene "010,020" \
  --shot "0010,0020,0030" \
  --task "comp,light" \
  --start_frame 1001 \
  --end_frame 1024
```

Or use a JSON template file:

```bash
fakeshot --template my_template.json
```

To see what a template looks like:

```bash
fakeshot --sample-template
```

### Custom naming patterns

You can change how files are organized and named using these options:

- `--path-pattern` - directory structure (default: `{show}/{scene}/{shot}/{task}/{version}`)
- `--file-pattern` - filename format (default: `{show}_{scene}_{shot}_{task}_{version}.{frame}`)

For example, if you want a flatter structure:

```bash
fakeshot --path-pattern "{show}/{shot}" --file-pattern "{shot}_{task}.{frame}"
```

This would create:

```
myproject/0010/0010_comp.1001.exr
myproject/0010/0010_comp.1002.exr
```
## Options

- `--out` - where to save files (default: ./out)
- `--show` - project name
- `--scene` - scene names (comma separated)
- `--shot` - shot names (comma separated)
- `--task` - task types (comma separated)
- `--version` - version string
- `--start_frame` / `--end_frame` - frame range
- `--width` / `--height` - image dimensions
- `--verbose` - more output
- `--file-pattern` - how to render the filename
- `--path-pattern` - how to render the path of the filename

## Why?

Sometimes you need a quick, throwable bunch of EXR files to test tools or directory structures.

The EXR files are just gray images with the filename in the middle, but they're real EXR files that should work with most tools.
