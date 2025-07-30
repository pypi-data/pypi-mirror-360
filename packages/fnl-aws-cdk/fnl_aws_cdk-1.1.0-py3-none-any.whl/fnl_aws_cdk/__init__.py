r'''
# Will be replacing this with project documentation
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

import aws_cdk.aws_opensearchservice as _aws_cdk_aws_opensearchservice_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="fnl-aws-cdk.OpensearchProps",
    jsii_struct_bases=[],
    name_mapping={
        "program": "program",
        "project": "project",
        "tier": "tier",
        "username": "username",
        "domain_props": "domainProps",
    },
)
class OpensearchProps:
    def __init__(
        self,
        *,
        program: builtins.str,
        project: builtins.str,
        tier: "Tier",
        username: builtins.str,
        domain_props: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.DomainProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param program: 
        :param project: 
        :param tier: 
        :param username: 
        :param domain_props: 
        '''
        if isinstance(domain_props, dict):
            domain_props = _aws_cdk_aws_opensearchservice_ceddda9d.DomainProps(**domain_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__974488af333c2fd8ca774a2398bd8d2566e9c9ca32c42a879da4af503bd5c16b)
            check_type(argname="argument program", value=program, expected_type=type_hints["program"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument tier", value=tier, expected_type=type_hints["tier"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument domain_props", value=domain_props, expected_type=type_hints["domain_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "program": program,
            "project": project,
            "tier": tier,
            "username": username,
        }
        if domain_props is not None:
            self._values["domain_props"] = domain_props

    @builtins.property
    def program(self) -> builtins.str:
        result = self._values.get("program")
        assert result is not None, "Required property 'program' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project(self) -> builtins.str:
        result = self._values.get("project")
        assert result is not None, "Required property 'project' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tier(self) -> "Tier":
        result = self._values.get("tier")
        assert result is not None, "Required property 'tier' is missing"
        return typing.cast("Tier", result)

    @builtins.property
    def username(self) -> builtins.str:
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.DomainProps]:
        result = self._values.get("domain_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.DomainProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpensearchProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpensearchService(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="fnl-aws-cdk.OpensearchService",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        program: builtins.str,
        project: builtins.str,
        tier: "Tier",
        username: builtins.str,
        domain_props: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.DomainProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param program: 
        :param project: 
        :param tier: 
        :param username: 
        :param domain_props: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ec7a363617dc53ede7da483ba6b1d80ac70d6b62719c8653fb355d0cecfbe60)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OpensearchProps(
            program=program,
            project=project,
            tier=tier,
            username=username,
            domain_props=domain_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.enum(jsii_type="fnl-aws-cdk.Tier")
class Tier(enum.Enum):
    DEV = "DEV"
    QA = "QA"
    STAGE = "STAGE"
    PROD = "PROD"


__all__ = [
    "OpensearchProps",
    "OpensearchService",
    "Tier",
]

publication.publish()

def _typecheckingstub__974488af333c2fd8ca774a2398bd8d2566e9c9ca32c42a879da4af503bd5c16b(
    *,
    program: builtins.str,
    project: builtins.str,
    tier: Tier,
    username: builtins.str,
    domain_props: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.DomainProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ec7a363617dc53ede7da483ba6b1d80ac70d6b62719c8653fb355d0cecfbe60(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    program: builtins.str,
    project: builtins.str,
    tier: Tier,
    username: builtins.str,
    domain_props: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.DomainProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
