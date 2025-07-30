# tushell

The Data Diver's best Intelligent and Narrative Command-Line Tooling you will have ever had.

## Description

`tushell` is a CLI-native, recursive DevOps & narrative command tooling package designed to provide intelligent and narrative libraries and command-line tooling for data divers.

## Installation

To install `tushell`, use pip:

```bash
pip install tushell
```

## Usage

### Implemented Commands

* `get-memory`: Retrieve memory by key, with advanced Markdown/JSON output options.

```bash
tushell get-memory --key <keyname> [--md|--md-file|--mkey|--jkey]
```

- `--md` : Output as Markdown to stdout
- `--md-file <filename>` : Output as Markdown to a file
- `--mkey <keyname>` : Output as Markdown using the key as fallback if `--key` is omitted
- `--jkey <keyname>` : Output as JSON using the key as fallback if `--key` is omitted

See the [Markdown Output Ritual](../../docs/OUTPUTS.md) for full details and best practices.

* `draw-memory-graph`: Print an ASCII-rendered graph of the memory keys and Arc structure.

```bash
tushell draw-memory-graph
```

### FUTURE COMMANDS

The following commands are planned but not yet fully implemented:

* `scan-nodes`: Simulate scanning and listing nodes in the system.
* `flex`: Demonstrate flexible orchestration of tasks.
* `trace-orbit`: Trace and visualize the orbit of data or processes.
* `echo-sync`: Synchronize data or processes across nodes.

---

#### Markdown Output Ritual

`tushell get-memory` supports a recursive Markdown output ritual:
- The key is always the first section.
- Nested `"value"` fields unfold as sub-sections.
- All Markdown output modes (`--md`, `--md-file`, `--mkey`) use this structure.

See [OUTPUTS.md](../../docs/OUTPUTS.md) for detailed examples and best practices.
