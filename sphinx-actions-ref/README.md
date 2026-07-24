# sphinx-actions-ref

A Sphinx extension that generates reference documentation from Juju charm
`actions.yaml` files.

## Features

- **Directive**: Use `.. actions-reference::` (reST) or `` {actions-reference} ``
  (MyST) to embed action documentation inline in any page.
- **Auto-generation**: Optionally write standalone `.md` or `.rst` files into the
  source tree at build time, keeping docs in sync with code automatically.
- **Multiple sources**: Document actions from multiple charms in the same
  documentation set.

## Installation

```bash
pip install sphinx-actions-ref
```

## Quick start

Add the extension to your Sphinx `conf.py`:

```python
extensions = [
    "sphinx_actions_ref",
]

# Path to your actions.yaml (relative to conf.py directory)
actions_sources = "actions.yaml"
```

### Using the directive

In a reST file:

```rst
.. actions-reference::
```

In a MyST file:

````md
```{actions-reference}
```
````

### Auto-generating standalone pages

```python
actions_autogenerate = True
actions_output_format = "myst"  # or "rst"
actions_sources = [
    {"yaml_path": "charms/foo/actions.yaml", "output_path": "reference/foo-actions"},
    {"yaml_path": "charms/bar/actions.yaml", "output_path": "reference/bar-actions"},
]
```

## Configuration

| Option | Type | Default | Description |
|---|---|---|---|
| `actions_sources` | `list[dict]` or `str` | `"actions.yaml"` | Source declarations. A bare string is shorthand for a single source. |
| `actions_output_format` | `str` | `"myst"` | `"myst"` for `.md`, `"rst"` for `.rst` |
| `actions_autogenerate` | `bool` | `False` | Write standalone files on build |

Each entry in `actions_sources` accepts:

| Key | Required | Default | Description |
|---|---|---|---|
| `yaml_path` | yes | — | Path to `actions.yaml`, relative to `confdir` |
| `output_path` | no | `"reference/actions"` | Output path relative to `srcdir` (no extension) |

## License

Apache-2.0
