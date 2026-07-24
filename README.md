# sphinx-charm-reference-generator

A Sphinx extension that renders Juju charm `actions.yaml` documentation inline
using a directive.

## Basic usage

### Directive

Use `.. actions-reference::` (reST) or `` {actions-reference} ``
(MyST) to embed action documentation inline in any page.

Multiple directive instances can document actions from multiple charms in the
same documentation set.

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

### Directive options

| Option             | Type  | Default           | Description                                                                                                                                     |
| ------------------ | ----- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `:action-sources:` | `str` | `../actions.yaml` | Path to an `actions.yaml` file, relative to the Sphinx source directory (the directory containing `conf.py`). Absolute paths are used as-is. |

## Project setup

sphinx-charm-reference-generator is published on PyPI and can be installed with:

```bash
pip install sphinx-charm-reference-generator
```

After installing, add the extension to your Sphinx `conf.py`:

```python
extensions = [
    "sphinx_charm_reference_generator",
]
```

## Community and support

You can report any issues or bugs on the project's [GitHub
repository](https://github.com/canonical/sphinx-charm-reference-generator).

sphinx-charm-reference-generator is covered by the [Ubuntu Code of
Conduct](https://ubuntu.com/community/ethos/code-of-conduct).

## License and copyright

sphinx-charm-reference-generator is released under the [GPL-3.0 license](LICENSE).

© 2025 Canonical Ltd.
