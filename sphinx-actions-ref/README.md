# sphinx-actions-ref

A Sphinx extension that renders Juju charm `actions.yaml` documentation inline
using a directive.

## Features

- **Directive**: Use `.. actions-reference::` (reST) or `` {actions-reference} ``
  (MyST) to embed action documentation inline in any page.
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

You can override the YAML path per directive instance:

```rst
.. actions-reference::
   :yaml-path: path/to/other/actions.yaml
```

## Configuration

| Option | Type | Default | Description |
|---|---|---|---|
| `actions_sources` | `list` or `str` | `"actions.yaml"` | Path(s) to `actions.yaml` files, relative to `confdir`. A bare string is shorthand for a single source. |
| `actions_confdir` | `str` | Sphinx `confdir` | Base directory for resolving relative paths |

## License

Apache-2.0
