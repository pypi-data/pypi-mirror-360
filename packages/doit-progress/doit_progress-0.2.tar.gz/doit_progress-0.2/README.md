markdown
# doit-progress

A command for the [doit](https://pydoit.org/) task management system that displays the overall progress of tasks in a visual progress bar.

## Installation

```bash
pip install doit-progress
```

## Usage

Once installed, the command is automatically registered with `doit`. You can use it by running:

```bash
doit progress
```

This will display a progress bar showing the completion status of all tasks defined in your `dodo.py` file. You can specify a different `dodo.py` file using the `-f` flag.

### Options

- `--bar-length`: Set the length of the progress bar (default: 50 characters)
- `--interactive`: Enable interactive mode with real-time progress updates

Example:
```bash
doit progress --bar-length 75
doit progress --interactive
```

## Requirements

- Python >= 3.8
- doit >= 0.36.0
- cloudpickle >= 3.1.1
- doit-sqlite-sync >= 1.0

## License

This project is licensed under the CeCILL-B License.