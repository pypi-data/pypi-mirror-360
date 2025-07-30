r'''
# TypeScript AWS CDK solution for setup a developer platform at AWS

This is TypeScript CDK constructs project to create an open source developer platform at AWS

## How it Works

This project uses projen for TypeScript sources, tooling and testing.
Just execute `npx projen help` to see what you can do.

**Current status:** Under development

## How to start

You will need to have Typescript 5.8 or newer version and Yarn installed.
This will also install AWS cdk command by calling `npm install -g aws-cdk`.

... Yada yada

main DevCloudConstruct

# cdk-dev-cloud-constructs

[![](https://constructs.dev/favicon.ico) Construct Hub](https://constructs.dev/packages/cdk-dev-cloud-constructs)

---


## Table of Contents

* [Installation](#installation)
* [License](#license)

## Installation

TypeScript/JavaScript:

```bash
npm i cdk-dev-cloud-constructs
```

Python:

```bash
pip install cdk-dev-cloud-constructs
```

## License

`cdk-pipeline-for-terraform` is distributed under the terms of the [MIT](https://opensource.org/license/mit/) license.

# replace this
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import constructs as _constructs_77d1e7e8


class GitlabConstruct(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-dev-cloud-constructs.GitlabConstruct",
):
    '''(experimental) VSCodeServer - spin it up in under 10 minutes.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain_name: (experimental) Gitlab full qualified domain name.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20b97d9969c599c19a466a004376fceb871af277a21d8ce6beea32fe12dd1da4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GitlabProps(domain_name=domain_name)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "domain", []))

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29bcde09d1c7a6e4f94ee946519b4cf29803bd2a639a61c71cc2bd07e8777f68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domainName", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="cdk-dev-cloud-constructs.GitlabProps",
    jsii_struct_bases=[],
    name_mapping={"domain_name": "domainName"},
)
class GitlabProps:
    def __init__(self, *, domain_name: typing.Optional[builtins.str] = None) -> None:
        '''(experimental) Properties for the Gitlab construct.

        :param domain_name: (experimental) Gitlab full qualified domain name.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74a002fc4709396e3fb919f7a515ced9e8876286c10d340756a4e473c09edd4f)
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if domain_name is not None:
            self._values["domain_name"] = domain_name

    @builtins.property
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Gitlab full qualified domain name.

        :stability: experimental
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitlabProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Hello(metaclass=jsii.JSIIMeta, jsii_type="cdk-dev-cloud-constructs.Hello"):
    '''
    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="sayHello")
    def say_hello(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "sayHello", []))


__all__ = [
    "GitlabConstruct",
    "GitlabProps",
    "Hello",
]

publication.publish()

def _typecheckingstub__20b97d9969c599c19a466a004376fceb871af277a21d8ce6beea32fe12dd1da4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29bcde09d1c7a6e4f94ee946519b4cf29803bd2a639a61c71cc2bd07e8777f68(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74a002fc4709396e3fb919f7a515ced9e8876286c10d340756a4e473c09edd4f(
    *,
    domain_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
