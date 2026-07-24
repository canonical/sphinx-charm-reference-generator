# sphinx-actions-ref

A Sphinx extension that renders Juju charm `actions.yaml` documentation inline
using a directive.

## Features

- **Directive**: Use `.. actions-reference::` (reST) or `` {actions-reference} ``
  (MyST) to embed action documentation inline in any page.
- **Multiple sources**: Document actions from multiple charms in the same
  documentation set by adding multiple directive instances.

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

By default, the directive looks for `actions.yaml` one level above the Sphinx
source directory (i.e. `../actions.yaml` relative to the directory containing
`conf.py`). This matches the common layout where docs live in a `docs/` folder
and `actions.yaml` is at the repository root:

```
my-charm/
    actions.yaml
    docs/
        conf.py
        index.rst
```

To point to a different file, use the `:action-sources:` option with a path
relative to the Sphinx source directory:

```rst
.. actions-reference::
   :action-sources: ../actions.yaml
```

For monorepos with multiple charms, use one directive per charm:

```rst
.. actions-reference::
   :action-sources: ../charm-a/actions.yaml

.. actions-reference::
   :action-sources: ../charm-b/actions.yaml
```

Absolute paths are also supported:

```rst
.. actions-reference::
   :action-sources: /home/user/project/actions.yaml
```

## Directive options

| Option | Type | Default | Description |
|---|---|---|---|
| `:action-sources:` | `str` | `../actions.yaml` | Path to an `actions.yaml` file, relative to the Sphinx source directory (the directory containing `conf.py`). Absolute paths are used as-is. |

## License

Apache-2.0
