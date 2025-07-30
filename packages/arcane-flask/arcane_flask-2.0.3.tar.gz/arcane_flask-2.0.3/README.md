# Arcane flask

This package help us authenticate users

## Get Started

```sh
pip install arcane-flask
```

## Example Usage

```python
from arcane import flask

@check_access_rights(service='function', required_rights='Viewer',
                     receive_rights_per_client=True, project=Config.Project, adscale_key=Config.Key)
def function(params):
    pass

```

