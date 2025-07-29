r'''
# WAF HTTP API

A CDK construct that fronts an HTTP API with a CloudFront distribution and protects it with AWS WAF.

## Features

* **Enhanced Security:** Protects your HTTP API with AWS WAF rules
* **Global CDN:** Fronts your API with CloudFront for improved performance and availability
* **Origin Verification:** Adds a secret header to ensure requests come through CloudFront
* **Customizable:** Use default WAF rules or provide your own custom rules
* **Easy Integration:** Simple to add to existing AWS CDK stacks

## Installation

### TypeScript/JavaScript

```bash
npm install waf-http-api
```

### Python

<!-- ```bash
pip install waf-http-api
``` -->

## Usage

This example shows how to protect an HTTP API with WAF and CloudFront:

```python
import { Stack, StackProps } from "aws-cdk-lib";
import { HttpApi, HttpMethod } from "aws-cdk-lib/aws-apigatewayv2";
import { HttpLambdaIntegration } from "aws-cdk-lib/aws-apigatewayv2-integrations";
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";
import { Runtime } from "aws-cdk-lib/aws-lambda";
import { WafHttpApi } from "waf-http-api";

class MyStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const myLambda = new NodejsFunction(this, "MyApiHandler", {
      runtime: Runtime.NODEJS_18_X,
      handler: "handler",
      entry: "lambda/handler.ts",
    });

    const httpApi = new HttpApi(this, "MyHttpApi", {
      description: "My example HTTP API",
    });

    httpApi.addRoutes({
      path: "/hello",
      methods: [HttpMethod.GET],
      integration: new HttpLambdaIntegration("MyLambdaIntegration", myLambda),
    });

    const protectedApi = new WafHttpApi(this, "ProtectedMyApi", {
      httpApi: httpApi,
      // Optionally, provide custom WAF rules:
      // wafRules: [ ... ],
    });

    new cdk.CfnOutput(this, "ProtectedApiEndpoint", {
      value: protectedApi.distribution.distributionDomainName,
      description: "The CloudFront URL for the protected API endpoint",
    });

    new cdk.CfnOutput(this, "OriginVerificationSecret", {
      value: protectedApi.secretHeaderValue,
      description: "Secret value to verify CloudFront origin requests",
    });
  }
}
```

## API

See [`API.md`](API.md) for full API documentation.

## Development

This project uses [projen](https://github.com/projen/projen) for project management. To synthesize project files after making changes to `.projenrc.ts`, run:

```bash
npx projen
```

## License

MIT © Merapar Technologies Group B.V.
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

import aws_cdk.aws_apigatewayv2 as _aws_cdk_aws_apigatewayv2_ceddda9d
import aws_cdk.aws_cloudfront as _aws_cdk_aws_cloudfront_ceddda9d
import aws_cdk.aws_wafv2 as _aws_cdk_aws_wafv2_ceddda9d
import constructs as _constructs_77d1e7e8


class WafHttpApi(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="waf-http-api.WafHttpApi",
):
    '''
    :class: WafHttpApi
    :description:

    A CDK construct that fronts an AWS HTTP API with a CloudFront distribution
    and protects it with AWS WAF. This enhances security and performance by
    adding a global CDN layer and web application firewall capabilities.
    It also injects a secret header from CloudFront to the origin to allow
    for origin verification by a Lambda Authorizer or similar mechanism.
    :extends: Construct
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        http_api: _aws_cdk_aws_apigatewayv2_ceddda9d.HttpApi,
        waf_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL.RuleProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: The scope in which to define this construct (e.g., a CDK Stack).
        :param id: The unique identifier for this construct within its scope.
        :param http_api: The HTTP API to be protected by the WAF and CloudFront. This should be an instance of ``aws-cdk-lib/aws-apigatewayv2.HttpApi``.
        :param waf_rules: Optional: Custom WAF rules to apply to the WebACL. If not provided, a default set of AWS Managed Rules will be used, specifically "AWSManagedRulesAmazonIpReputationList" and "AWSManagedRulesCommonRuleSet". These rules help protect against common web exploits and unwanted traffic. Default: AWS Managed Rules (AmazonIpReputationList, CommonRuleSet)

        :constructor: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d85ac6423dea7afad65ba02061fbf680d6c1e47b52cc21989650da33e763be0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WafHttpApiProps(http_api=http_api, waf_rules=waf_rules)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="SECRET_HEADER_NAME")
    def SECRET_HEADER_NAME(cls) -> builtins.str:
        '''
        :description:

        The name of the custom header CloudFront will add to requests
        forwarded to the origin. This header can be used by your backend (e.g.,
        a Lambda Authorizer for API Gateway) to verify that the request originated
        from CloudFront and not directly from the internet.
        :property: {string} SECRET_HEADER_NAME
        :readonly: true
        :static: true
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "SECRET_HEADER_NAME"))

    @builtins.property
    @jsii.member(jsii_name="distribution")
    def distribution(self) -> _aws_cdk_aws_cloudfront_ceddda9d.Distribution:
        '''
        :description:

        The CloudFront distribution created and managed by this construct.
        You can use this property to retrieve the distribution's domain name or ARN.
        :property: {cloudfront.Distribution} distribution
        :readonly: true
        '''
        return typing.cast(_aws_cdk_aws_cloudfront_ceddda9d.Distribution, jsii.get(self, "distribution"))

    @builtins.property
    @jsii.member(jsii_name="secretHeaderValue")
    def secret_header_value(self) -> builtins.str:
        '''
        :description:

        The randomly generated secret value for the custom header.
        This value is unique for each deployment of the construct.
        It should be used in your HTTP API's authorizer or backend logic
        to validate requests coming through CloudFront.
        :property: {string} secretHeaderValue
        :readonly: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretHeaderValue"))


@jsii.data_type(
    jsii_type="waf-http-api.WafHttpApiProps",
    jsii_struct_bases=[],
    name_mapping={"http_api": "httpApi", "waf_rules": "wafRules"},
)
class WafHttpApiProps:
    def __init__(
        self,
        *,
        http_api: _aws_cdk_aws_apigatewayv2_ceddda9d.HttpApi,
        waf_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL.RuleProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param http_api: The HTTP API to be protected by the WAF and CloudFront. This should be an instance of ``aws-cdk-lib/aws-apigatewayv2.HttpApi``.
        :param waf_rules: Optional: Custom WAF rules to apply to the WebACL. If not provided, a default set of AWS Managed Rules will be used, specifically "AWSManagedRulesAmazonIpReputationList" and "AWSManagedRulesCommonRuleSet". These rules help protect against common web exploits and unwanted traffic. Default: AWS Managed Rules (AmazonIpReputationList, CommonRuleSet)

        :description: Properties for the ``WafForHttpApi`` construct.
        :interface: WafHttpApiProps
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd0c48f02a0f3dbd44bbc23e0a023c8d596dcba9ca17bc8c97e123086b4cdef3)
            check_type(argname="argument http_api", value=http_api, expected_type=type_hints["http_api"])
            check_type(argname="argument waf_rules", value=waf_rules, expected_type=type_hints["waf_rules"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "http_api": http_api,
        }
        if waf_rules is not None:
            self._values["waf_rules"] = waf_rules

    @builtins.property
    def http_api(self) -> _aws_cdk_aws_apigatewayv2_ceddda9d.HttpApi:
        '''The HTTP API to be protected by the WAF and CloudFront.

        This should be an instance of ``aws-cdk-lib/aws-apigatewayv2.HttpApi``.

        :type: {HttpApi}
        '''
        result = self._values.get("http_api")
        assert result is not None, "Required property 'http_api' is missing"
        return typing.cast(_aws_cdk_aws_apigatewayv2_ceddda9d.HttpApi, result)

    @builtins.property
    def waf_rules(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL.RuleProperty]]:
        '''Optional: Custom WAF rules to apply to the WebACL.

        If not provided, a default set of AWS Managed Rules will be used,
        specifically "AWSManagedRulesAmazonIpReputationList" and "AWSManagedRulesCommonRuleSet".
        These rules help protect against common web exploits and unwanted traffic.

        :default: AWS Managed Rules (AmazonIpReputationList, CommonRuleSet)

        :type: {wafv2.CfnWebACL.RuleProperty[]}
        '''
        result = self._values.get("waf_rules")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL.RuleProperty]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WafHttpApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "WafHttpApi",
    "WafHttpApiProps",
]

publication.publish()

def _typecheckingstub__0d85ac6423dea7afad65ba02061fbf680d6c1e47b52cc21989650da33e763be0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    http_api: _aws_cdk_aws_apigatewayv2_ceddda9d.HttpApi,
    waf_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL.RuleProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd0c48f02a0f3dbd44bbc23e0a023c8d596dcba9ca17bc8c97e123086b4cdef3(
    *,
    http_api: _aws_cdk_aws_apigatewayv2_ceddda9d.HttpApi,
    waf_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_wafv2_ceddda9d.CfnWebACL.RuleProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass
