# sag_py_auth

[![Maintainability][codeclimate-image]][codeclimate-url]
[![Coverage Status][coveralls-image]][coveralls-url]
[![Known Vulnerabilities](https://snyk.io/test/github/SamhammerAG/sag_py_auth/badge.svg)](https://snyk.io/test/github/SamhammerAG/sag_py_auth)

[coveralls-image]:https://coveralls.io/repos/github/SamhammerAG/sag_py_auth/badge.svg?branch=master
[coveralls-url]:https://coveralls.io/github/SamhammerAG/sag_py_auth?branch=master
[codeclimate-image]:https://api.codeclimate.com/v1/badges/2da48e3952f9640f702f/maintainability
[codeclimate-url]:https://codeclimate.com/github/SamhammerAG/sag_py_auth/maintainability

This provides a way to secure your fastapi with keycloak jwt bearer authentication.

## What it does
* Secure your api endpoints
* Verifies auth tokens: signature, expiration, issuer, audience
* Allows to set permissions by specifying roles and realm roles

## How to use

### Installation

pip install sag-py-auth

### Secure your apis

First create the fast api dependency with the auth config:
```python
from sag_py_auth.models import AuthConfig, TokenRole
from sag_py_auth.jwt_auth import JwtAuth
from fastapi import Depends

auth_config = AuthConfig("https://authserver.com/auth/realms/projectName", "myaudience")
required_roles = [TokenRole("clientname", "adminrole")]
required_realm_roles = ["additionalrealmrole"]
requires_admin = Depends(JwtAuth(auth_config, required_roles, required_realm_roles))
```

Afterwards you can use it in your route like that:

```python
@app.post("/posts", dependencies=[requires_admin], tags=["posts"])
async def add_post(post: PostSchema) -> dict:
```

Or if you use sub routes, auth can also be enforced for the entire route like that:

```python
router = APIRouter()
router.include_router(sub_router, tags=["my_api_tag"], prefix="/subroute",dependencies=[requires_admin])
```

### Get user information

The Jwt call directly returns a token object that can be used to get additional information.

Furthermore you can access the context directly:
```python
from sag_py_auth.auth_context import get_token as get_token_from_context
token = get_token_from_context()
```

This works in async calls but not in sub threads (without additional changes).

See:
* https://docs.python.org/3/library/contextvars.html
* https://kobybass.medium.com/python-contextvars-and-multithreading-faa33dbe953d

#### Methods available on the token object

* get_field_value: to get the value of a claim field (or an empty string if not present)
* get_roles: Gets the roles of a specific client
* has_role: Verify if a spcific client has a role
* get_realm_roles: Get the realm roles
* has_realm_role: Check if the user has a specific realm role


### Log user data

It is possible to log the preferred_username and the azp value (party that created the token) of the token by adding a filter.

```python
import logging
from sag_py_auth import UserNameLoggingFilter

console_handler = logging.StreamHandler(sys.stdout)
console_handler.addFilter(UserNameLoggingFilter())

```

The filter provides the following two fields as soon as the user is authenticated: user_name, authorized_party

### How a token has to look like

```json
{

    "iss": "https://authserver.com/auth/realms/projectName",
    "aud": ["audienceOne", "audienceTwo"],
    "typ": "Bearer",
    "azp": "public-project-swagger",
    "preferred_username": "preferredUsernameValue",
    .....
    "realm_access": {
        "roles": ["myRealmRoleOne"]
    },
    "resource_access": {
        "my-client-one": {
            "roles": ["a-permission-role", "user"]
        },
        "my-client-two": {
            "roles": ["a-permission-role", "admin"]
        }
    }
}
```

* realm_access contains the realm roles
* resource_access contains the token roles for one or multiple clients

## How to start developing

### With vscode

Just install vscode with dev containers extension. All required extensions and configurations are prepared automatically.

### With pycharm

* Install latest pycharm
* Install pycharm plugin BlackConnect
* Install pycharm plugin Mypy
* Configure the python interpreter/venv
* pip install requirements-dev.txt
* pip install black[d]
* Ctl+Alt+S => Check Tools => BlackConnect => Trigger when saving changed files
* Ctl+Alt+S => Check Tools => BlackConnect => Trigger on code reformat
* Ctl+Alt+S => Click Tools => BlackConnect => "Load from pyproject.yaml" (ensure line length is 120)
* Ctl+Alt+S => Click Tools => BlackConnect => Configure path to the blackd.exe at the "local instance" config (e.g. C:\Python310\Scripts\blackd.exe)
* Ctl+Alt+S => Click Tools => Actions on save => Reformat code
* Restart pycharm

## How to publish
* Update the version in setup.py and commit your change
* Create a tag with the same version number
* Let github do the rest
