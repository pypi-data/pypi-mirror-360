r'''
# CDK ECS CodeDeploy

[![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg)](https://constructs.dev/packages/@cdklabs/cdk-ecs-codedeploy)
[![npm version](https://badge.fury.io/js/@cdklabs%2Fcdk-ecs-codedeploy.svg)](https://badge.fury.io/js/@cdklabs%2Fcdk-ecs-codedeploy)
[![Maven Central](https://maven-badges.herokuapp.com/maven-central/io.github.cdklabs/cdk-ecs-codedeploy/badge.svg)](https://maven-badges.herokuapp.com/maven-central/io.github.cdklabs/cdk-ecs-codedeploy)
[![PyPI version](https://badge.fury.io/py/cdklabs.ecs-codedeploy.svg)](https://badge.fury.io/py/cdklabs.ecs-codedeploy)
[![NuGet version](https://badge.fury.io/nu/Cdklabs.CdkEcsCodeDeploy.svg)](https://badge.fury.io/nu/Cdklabs.CdkEcsCodeDeploy)
[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/cdklabs/cdk-ecs-codedeploy)
[![Mergify](https://img.shields.io/endpoint.svg?url=https://api.mergify.com/badges/cdklabs/cdk-ecs-codedeploy&style=flat)](https://mergify.io)

This project contains CDK constructs to create CodeDeploy ECS deployments.

## Installation

<details><summary><strong>TypeScript</strong></summary>

```bash
yarn add @cdklabs/cdk-ecs-codedeploy
```

</details><details><summary><strong>Java</strong></summary>

See https://mvnrepository.com/artifact/io.github.cdklabs/cdk-ecs-codedeploy

</details><details><summary><strong>Python</strong></summary>

See https://pypi.org/project/cdklabs.ecs-codedeploy/

</details><details><summary><strong>C#</strong></summary>

See https://www.nuget.org/packages/Cdklabs.CdkEcsCodeDeploy/

</details>

### Deployments

CodeDeploy for ECS can manage the deployment of new task definitions to ECS services.  Only 1 deployment construct can be defined for a given EcsDeploymentGroup.

```python
# deployment_group: codeDeploy.IEcsDeploymentGroup
# task_definition: ecs.ITaskDefinition


EcsDeployment(
    deployment_group=deployment_group,
    target_service=TargetService(
        task_definition=task_definition,
        container_name="mycontainer",
        container_port=80
    )
)
```

The deployment will use the AutoRollbackConfig for the EcsDeploymentGroup unless it is overridden in the deployment:

```python
# deployment_group: codeDeploy.IEcsDeploymentGroup
# task_definition: ecs.ITaskDefinition


EcsDeployment(
    deployment_group=deployment_group,
    target_service=TargetService(
        task_definition=task_definition,
        container_name="mycontainer",
        container_port=80
    ),
    auto_rollback=codeDeploy.AutoRollbackConfig(
        failed_deployment=True,
        deployment_in_alarm=True,
        stopped_deployment=False
    )
)
```

By default, the deployment will timeout after 30 minutes. The timeout value can be overridden:

```python
# deployment_group: codeDeploy.IEcsDeploymentGroup
# task_definition: ecs.ITaskDefinition


EcsDeployment(
    deployment_group=deployment_group,
    target_service=TargetService(
        task_definition=task_definition,
        container_name="mycontainer",
        container_port=80
    ),
    timeout=Duration.minutes(60)
)
```

### API Canaries

CodeDeploy can leverage Cloudwatch Alarms to trigger automatic rollbacks. The `ApiCanary` construct simplifies the process for creating CloudWatch Synthetics Canaries to monitor APIs. The following code demonstrates a canary that monitors https://xkcd.com/908/info.0.json and checks the JSON response to assert that `safe_title` has the value of `'The Cloud'`.

```python
canary = ApiCanary(stack, "Canary",
    base_url="https://xkcd.com",
    duration_alarm_threshold=Duration.seconds(5),
    thread_count=5,
    steps=[ApiTestStep(
        name="info",
        path="/908/info.0.json",
        jmes_path="safe_title",
        expected_value="The Cloud"
    )
    ]
)
```

### Application Load Balanced CodeDeployed Fargate Service

An L3 construct named `ApplicationLoadBalancedCodeDeployedFargateService` extends [ApplicationLoadBalancedFargateService](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ecs_patterns.ApplicationLoadBalancedFargateService.html) and adds support for deploying new versions of the service with AWS CodeDeploy. Additionally, an Amazon CloudWatch Synthetic canary is created via the `ApiCanary` construct and is monitored by the CodeDeploy deployment to trigger rollback if the canary begins to alarm.

```python
# cluster: ecs.ICluster
# image: ecs.ContainerImage

service = ApplicationLoadBalancedCodeDeployedFargateService(stack, "Service",
    cluster=cluster,
    task_image_options=ApplicationLoadBalancedTaskImageOptions(
        image=image
    ),
    api_test_steps=[ApiTestStep(
        name="health",
        path="/health",
        jmes_path="status",
        expected_value="ok"
    )]
)
```

## Local Development

```bash
yarn install
yarn build
yarn test
```

To run an integration test and update the snapshot, run:

```bash
yarn integ:ecs-deployment:deploy
```

To recreate snapshots for integration tests, run:

```bash
yarn integ:snapshot-all
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_codedeploy as _aws_cdk_aws_codedeploy_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import aws_cdk.aws_ecs_patterns as _aws_cdk_aws_ecs_patterns_ceddda9d
import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_synthetics as _aws_cdk_aws_synthetics_ceddda9d
import constructs as _constructs_77d1e7e8


class ApiCanary(
    _aws_cdk_aws_synthetics_ceddda9d.Canary,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-ecs-codedeploy.ApiCanary",
):
    '''(experimental) A CloudWatch Synthetic Canary for monitoring APIs.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        base_url: builtins.str,
        artifacts_bucket_location: typing.Optional[typing.Union[_aws_cdk_aws_synthetics_ceddda9d.ArtifactsBucketLocation, typing.Dict[builtins.str, typing.Any]]] = None,
        canary_name: typing.Optional[builtins.str] = None,
        duration_alarm_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        failure_retention_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        schedule: typing.Optional[_aws_cdk_aws_synthetics_ceddda9d.Schedule] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        start_after_creation: typing.Optional[builtins.bool] = None,
        steps: typing.Optional[typing.Sequence[typing.Union["ApiTestStep", typing.Dict[builtins.str, typing.Any]]]] = None,
        success_retention_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        thread_count: typing.Optional[jsii.Number] = None,
        time_to_live: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param base_url: (experimental) The base URL to use for tests.
        :param artifacts_bucket_location: (experimental) The s3 location that stores the data of the canary runs. Default: - A new s3 bucket will be created without a prefix.
        :param canary_name: (experimental) The name of the canary. Be sure to give it a descriptive name that distinguishes it from other canaries in your account. Do not include secrets or proprietary information in your canary name. The canary name makes up part of the canary ARN, which is included in outbound calls over the internet. Default: - A unique name will be generated from the construct ID
        :param duration_alarm_threshold: (experimental) The threshold for triggering an alarm on the test duration. Default: - no alarm is created for duration
        :param failure_retention_period: (experimental) How many days should failed runs be retained. Default: Duration.days(31)
        :param role: (experimental) Canary execution role. This is the role that will be assumed by the canary upon execution. It controls the permissions that the canary will have. The role must be assumable by the AWS Lambda service principal. If not supplied, a role will be created with all the required permissions. If you provide a Role, you must add the required permissions. Default: - A unique role will be generated for this canary. You can add permissions to roles by calling 'addToRolePolicy'.
        :param schedule: (experimental) Specify the schedule for how often the canary runs. For example, if you set ``schedule`` to ``rate(10 minutes)``, then the canary will run every 10 minutes. You can set the schedule with ``Schedule.rate(Duration)`` (recommended) or you can specify an expression using ``Schedule.expression()``. Default: 'rate(5 minutes)'
        :param security_groups: (experimental) The list of security groups to associate with the canary's network interfaces. You must provide ``vpc`` when using this prop. Default: - If the canary is placed within a VPC and a security group is not specified a dedicated security group will be created for this canary.
        :param start_after_creation: (experimental) Whether or not the canary should start after creation. Default: true
        :param steps: (experimental) The steps to perform in the synthetic test.
        :param success_retention_period: (experimental) How many days should successful runs be retained. Default: Duration.days(31)
        :param thread_count: (experimental) The number of threads to run concurrently for the synthetic test. Default: - 20
        :param time_to_live: (experimental) How long the canary will be in a 'RUNNING' state. For example, if you set ``timeToLive`` to be 1 hour and ``schedule`` to be ``rate(10 minutes)``, your canary will run at 10 minute intervals for an hour, for a total of 6 times. Default: - no limit
        :param vpc: (experimental) The VPC where this canary is run. Specify this if the canary needs to access resources in a VPC. Default: - Not in VPC
        :param vpc_subnets: (experimental) Where to place the network interfaces within the VPC. You must provide ``vpc`` when using this prop. Default: - the Vpc default strategy if not specified

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__191f9116e56adec234abc14306f9567b253f56a52ebb603f3f2db855fff52cbc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ApiCanaryProps(
            base_url=base_url,
            artifacts_bucket_location=artifacts_bucket_location,
            canary_name=canary_name,
            duration_alarm_threshold=duration_alarm_threshold,
            failure_retention_period=failure_retention_period,
            role=role,
            schedule=schedule,
            security_groups=security_groups,
            start_after_creation=start_after_creation,
            steps=steps,
            success_retention_period=success_retention_period,
            thread_count=thread_count,
            time_to_live=time_to_live,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addTestStep")
    def add_test_step(
        self,
        *,
        name: builtins.str,
        path: builtins.str,
        body: typing.Optional[builtins.str] = None,
        expected_value: typing.Any = None,
        headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        jmes_path: typing.Optional[builtins.str] = None,
        method: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Add a new test step to this canary.

        :param name: (experimental) Name of test.
        :param path: (experimental) Path of HTTP request, relative to baseUrl.
        :param body: (experimental) Optional body to include in HTTP request. Default: - no body included.
        :param expected_value: (experimental) Expected value to compare against the jmesPath. Default: - undefined
        :param headers: (experimental) Optional headers to include in HTTP request. Default: - no headers included.
        :param jmes_path: (experimental) JMESPath to apply against the response from the HTTP request and compare against expected value. Default: - no JMESPath assertion will be performed.
        :param method: (experimental) Optional method to for HTTP request. Default: - GET

        :stability: experimental
        '''
        step = ApiTestStep(
            name=name,
            path=path,
            body=body,
            expected_value=expected_value,
            headers=headers,
            jmes_path=jmes_path,
            method=method,
        )

        return typing.cast(None, jsii.invoke(self, "addTestStep", [step]))

    @builtins.property
    @jsii.member(jsii_name="successAlarm")
    def success_alarm(self) -> _aws_cdk_aws_cloudwatch_ceddda9d.Alarm:
        '''(experimental) A CloudWatch Alarm that triggers when the success rate falls below 100% over the past 2 periods.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Alarm, jsii.get(self, "successAlarm"))

    @success_alarm.setter
    def success_alarm(self, value: _aws_cdk_aws_cloudwatch_ceddda9d.Alarm) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8421acef4559e3bdccb095c272a6b29bf9e4dd210557d600e8932b033d21e07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "successAlarm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="durationAlarm")
    def duration_alarm(self) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Alarm]:
        '''(experimental) A CloudWatch Alarm that triggers when the duration of the tests exceeds the given threshold over the past 2 periods.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Alarm], jsii.get(self, "durationAlarm"))

    @duration_alarm.setter
    def duration_alarm(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Alarm],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44a7b96ff37721539a356fa80f06c31f2594735a95565d63e168dc4160b4caf5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "durationAlarm", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdklabs/cdk-ecs-codedeploy.ApiCanaryProps",
    jsii_struct_bases=[],
    name_mapping={
        "base_url": "baseUrl",
        "artifacts_bucket_location": "artifactsBucketLocation",
        "canary_name": "canaryName",
        "duration_alarm_threshold": "durationAlarmThreshold",
        "failure_retention_period": "failureRetentionPeriod",
        "role": "role",
        "schedule": "schedule",
        "security_groups": "securityGroups",
        "start_after_creation": "startAfterCreation",
        "steps": "steps",
        "success_retention_period": "successRetentionPeriod",
        "thread_count": "threadCount",
        "time_to_live": "timeToLive",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
    },
)
class ApiCanaryProps:
    def __init__(
        self,
        *,
        base_url: builtins.str,
        artifacts_bucket_location: typing.Optional[typing.Union[_aws_cdk_aws_synthetics_ceddda9d.ArtifactsBucketLocation, typing.Dict[builtins.str, typing.Any]]] = None,
        canary_name: typing.Optional[builtins.str] = None,
        duration_alarm_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        failure_retention_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        schedule: typing.Optional[_aws_cdk_aws_synthetics_ceddda9d.Schedule] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        start_after_creation: typing.Optional[builtins.bool] = None,
        steps: typing.Optional[typing.Sequence[typing.Union["ApiTestStep", typing.Dict[builtins.str, typing.Any]]]] = None,
        success_retention_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        thread_count: typing.Optional[jsii.Number] = None,
        time_to_live: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param base_url: (experimental) The base URL to use for tests.
        :param artifacts_bucket_location: (experimental) The s3 location that stores the data of the canary runs. Default: - A new s3 bucket will be created without a prefix.
        :param canary_name: (experimental) The name of the canary. Be sure to give it a descriptive name that distinguishes it from other canaries in your account. Do not include secrets or proprietary information in your canary name. The canary name makes up part of the canary ARN, which is included in outbound calls over the internet. Default: - A unique name will be generated from the construct ID
        :param duration_alarm_threshold: (experimental) The threshold for triggering an alarm on the test duration. Default: - no alarm is created for duration
        :param failure_retention_period: (experimental) How many days should failed runs be retained. Default: Duration.days(31)
        :param role: (experimental) Canary execution role. This is the role that will be assumed by the canary upon execution. It controls the permissions that the canary will have. The role must be assumable by the AWS Lambda service principal. If not supplied, a role will be created with all the required permissions. If you provide a Role, you must add the required permissions. Default: - A unique role will be generated for this canary. You can add permissions to roles by calling 'addToRolePolicy'.
        :param schedule: (experimental) Specify the schedule for how often the canary runs. For example, if you set ``schedule`` to ``rate(10 minutes)``, then the canary will run every 10 minutes. You can set the schedule with ``Schedule.rate(Duration)`` (recommended) or you can specify an expression using ``Schedule.expression()``. Default: 'rate(5 minutes)'
        :param security_groups: (experimental) The list of security groups to associate with the canary's network interfaces. You must provide ``vpc`` when using this prop. Default: - If the canary is placed within a VPC and a security group is not specified a dedicated security group will be created for this canary.
        :param start_after_creation: (experimental) Whether or not the canary should start after creation. Default: true
        :param steps: (experimental) The steps to perform in the synthetic test.
        :param success_retention_period: (experimental) How many days should successful runs be retained. Default: Duration.days(31)
        :param thread_count: (experimental) The number of threads to run concurrently for the synthetic test. Default: - 20
        :param time_to_live: (experimental) How long the canary will be in a 'RUNNING' state. For example, if you set ``timeToLive`` to be 1 hour and ``schedule`` to be ``rate(10 minutes)``, your canary will run at 10 minute intervals for an hour, for a total of 6 times. Default: - no limit
        :param vpc: (experimental) The VPC where this canary is run. Specify this if the canary needs to access resources in a VPC. Default: - Not in VPC
        :param vpc_subnets: (experimental) Where to place the network interfaces within the VPC. You must provide ``vpc`` when using this prop. Default: - the Vpc default strategy if not specified

        :stability: experimental
        '''
        if isinstance(artifacts_bucket_location, dict):
            artifacts_bucket_location = _aws_cdk_aws_synthetics_ceddda9d.ArtifactsBucketLocation(**artifacts_bucket_location)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88653fc398cb7758d2ca950230ea75e3ed2418d64533c67731fcb689cc5e7fc9)
            check_type(argname="argument base_url", value=base_url, expected_type=type_hints["base_url"])
            check_type(argname="argument artifacts_bucket_location", value=artifacts_bucket_location, expected_type=type_hints["artifacts_bucket_location"])
            check_type(argname="argument canary_name", value=canary_name, expected_type=type_hints["canary_name"])
            check_type(argname="argument duration_alarm_threshold", value=duration_alarm_threshold, expected_type=type_hints["duration_alarm_threshold"])
            check_type(argname="argument failure_retention_period", value=failure_retention_period, expected_type=type_hints["failure_retention_period"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument start_after_creation", value=start_after_creation, expected_type=type_hints["start_after_creation"])
            check_type(argname="argument steps", value=steps, expected_type=type_hints["steps"])
            check_type(argname="argument success_retention_period", value=success_retention_period, expected_type=type_hints["success_retention_period"])
            check_type(argname="argument thread_count", value=thread_count, expected_type=type_hints["thread_count"])
            check_type(argname="argument time_to_live", value=time_to_live, expected_type=type_hints["time_to_live"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "base_url": base_url,
        }
        if artifacts_bucket_location is not None:
            self._values["artifacts_bucket_location"] = artifacts_bucket_location
        if canary_name is not None:
            self._values["canary_name"] = canary_name
        if duration_alarm_threshold is not None:
            self._values["duration_alarm_threshold"] = duration_alarm_threshold
        if failure_retention_period is not None:
            self._values["failure_retention_period"] = failure_retention_period
        if role is not None:
            self._values["role"] = role
        if schedule is not None:
            self._values["schedule"] = schedule
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if start_after_creation is not None:
            self._values["start_after_creation"] = start_after_creation
        if steps is not None:
            self._values["steps"] = steps
        if success_retention_period is not None:
            self._values["success_retention_period"] = success_retention_period
        if thread_count is not None:
            self._values["thread_count"] = thread_count
        if time_to_live is not None:
            self._values["time_to_live"] = time_to_live
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def base_url(self) -> builtins.str:
        '''(experimental) The base URL to use for tests.

        :stability: experimental
        '''
        result = self._values.get("base_url")
        assert result is not None, "Required property 'base_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def artifacts_bucket_location(
        self,
    ) -> typing.Optional[_aws_cdk_aws_synthetics_ceddda9d.ArtifactsBucketLocation]:
        '''(experimental) The s3 location that stores the data of the canary runs.

        :default: - A new s3 bucket will be created without a prefix.

        :stability: experimental
        '''
        result = self._values.get("artifacts_bucket_location")
        return typing.cast(typing.Optional[_aws_cdk_aws_synthetics_ceddda9d.ArtifactsBucketLocation], result)

    @builtins.property
    def canary_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the canary.

        Be sure to give it a descriptive name that distinguishes it from
        other canaries in your account.

        Do not include secrets or proprietary information in your canary name. The canary name
        makes up part of the canary ARN, which is included in outbound calls over the internet.

        :default: - A unique name will be generated from the construct ID

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/servicelens_canaries_security.html
        :stability: experimental
        '''
        result = self._values.get("canary_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def duration_alarm_threshold(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The threshold for triggering an alarm on the test duration.

        :default: - no alarm is created for duration

        :stability: experimental
        '''
        result = self._values.get("duration_alarm_threshold")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def failure_retention_period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) How many days should failed runs be retained.

        :default: Duration.days(31)

        :stability: experimental
        '''
        result = self._values.get("failure_retention_period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) Canary execution role.

        This is the role that will be assumed by the canary upon execution.
        It controls the permissions that the canary will have. The role must
        be assumable by the AWS Lambda service principal.

        If not supplied, a role will be created with all the required permissions.
        If you provide a Role, you must add the required permissions.

        :default:

        - A unique role will be generated for this canary.
        You can add permissions to roles by calling 'addToRolePolicy'.

        :see: required permissions: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-executionrolearn
        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def schedule(self) -> typing.Optional[_aws_cdk_aws_synthetics_ceddda9d.Schedule]:
        '''(experimental) Specify the schedule for how often the canary runs.

        For example, if you set ``schedule`` to ``rate(10 minutes)``, then the canary will run every 10 minutes.
        You can set the schedule with ``Schedule.rate(Duration)`` (recommended) or you can specify an expression using ``Schedule.expression()``.

        :default: 'rate(5 minutes)'

        :stability: experimental
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_synthetics_ceddda9d.Schedule], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''(experimental) The list of security groups to associate with the canary's network interfaces.

        You must provide ``vpc`` when using this prop.

        :default:

        - If the canary is placed within a VPC and a security group is
        not specified a dedicated security group will be created for this canary.

        :stability: experimental
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def start_after_creation(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether or not the canary should start after creation.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("start_after_creation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def steps(self) -> typing.Optional[typing.List["ApiTestStep"]]:
        '''(experimental) The steps to perform in the synthetic test.

        :stability: experimental
        '''
        result = self._values.get("steps")
        return typing.cast(typing.Optional[typing.List["ApiTestStep"]], result)

    @builtins.property
    def success_retention_period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) How many days should successful runs be retained.

        :default: Duration.days(31)

        :stability: experimental
        '''
        result = self._values.get("success_retention_period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def thread_count(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of threads to run concurrently for the synthetic test.

        :default: - 20

        :stability: experimental
        '''
        result = self._values.get("thread_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def time_to_live(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) How long the canary will be in a 'RUNNING' state.

        For example, if you set ``timeToLive`` to be 1 hour and ``schedule`` to be ``rate(10 minutes)``,
        your canary will run at 10 minute intervals for an hour, for a total of 6 times.

        :default: - no limit

        :stability: experimental
        '''
        result = self._values.get("time_to_live")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) The VPC where this canary is run.

        Specify this if the canary needs to access resources in a VPC.

        :default: - Not in VPC

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) Where to place the network interfaces within the VPC.

        You must provide ``vpc`` when using this prop.

        :default: - the Vpc default strategy if not specified

        :stability: experimental
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiCanaryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-ecs-codedeploy.ApiTestStep",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "path": "path",
        "body": "body",
        "expected_value": "expectedValue",
        "headers": "headers",
        "jmes_path": "jmesPath",
        "method": "method",
    },
)
class ApiTestStep:
    def __init__(
        self,
        *,
        name: builtins.str,
        path: builtins.str,
        body: typing.Optional[builtins.str] = None,
        expected_value: typing.Any = None,
        headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        jmes_path: typing.Optional[builtins.str] = None,
        method: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: (experimental) Name of test.
        :param path: (experimental) Path of HTTP request, relative to baseUrl.
        :param body: (experimental) Optional body to include in HTTP request. Default: - no body included.
        :param expected_value: (experimental) Expected value to compare against the jmesPath. Default: - undefined
        :param headers: (experimental) Optional headers to include in HTTP request. Default: - no headers included.
        :param jmes_path: (experimental) JMESPath to apply against the response from the HTTP request and compare against expected value. Default: - no JMESPath assertion will be performed.
        :param method: (experimental) Optional method to for HTTP request. Default: - GET

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d90c3a4104ecc8b3454055531f4b23054219c9454abf72a0f58b4992241a296)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument body", value=body, expected_type=type_hints["body"])
            check_type(argname="argument expected_value", value=expected_value, expected_type=type_hints["expected_value"])
            check_type(argname="argument headers", value=headers, expected_type=type_hints["headers"])
            check_type(argname="argument jmes_path", value=jmes_path, expected_type=type_hints["jmes_path"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "path": path,
        }
        if body is not None:
            self._values["body"] = body
        if expected_value is not None:
            self._values["expected_value"] = expected_value
        if headers is not None:
            self._values["headers"] = headers
        if jmes_path is not None:
            self._values["jmes_path"] = jmes_path
        if method is not None:
            self._values["method"] = method

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) Name of test.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''(experimental) Path of HTTP request, relative to baseUrl.

        :stability: experimental
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def body(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional body to include in HTTP request.

        :default: - no body included.

        :stability: experimental
        '''
        result = self._values.get("body")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expected_value(self) -> typing.Any:
        '''(experimental) Expected value to compare against the jmesPath.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("expected_value")
        return typing.cast(typing.Any, result)

    @builtins.property
    def headers(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Optional headers to include in HTTP request.

        :default: - no headers included.

        :stability: experimental
        '''
        result = self._values.get("headers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def jmes_path(self) -> typing.Optional[builtins.str]:
        '''(experimental) JMESPath to apply against the response from the HTTP request and compare against expected value.

        :default: - no JMESPath assertion will be performed.

        :stability: experimental
        '''
        result = self._values.get("jmes_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def method(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional method to for HTTP request.

        :default: - GET

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiTestStep(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-ecs-codedeploy.AppSpecHooks",
    jsii_struct_bases=[],
    name_mapping={
        "after_allow_test_traffic": "afterAllowTestTraffic",
        "after_allow_traffic": "afterAllowTraffic",
        "after_install": "afterInstall",
        "before_allow_traffic": "beforeAllowTraffic",
        "before_install": "beforeInstall",
    },
)
class AppSpecHooks:
    def __init__(
        self,
        *,
        after_allow_test_traffic: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
        after_allow_traffic: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
        after_install: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
        before_allow_traffic: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
        before_install: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
    ) -> None:
        '''(experimental) Lifecycle hooks configuration.

        :param after_allow_test_traffic: (experimental) Lambda or ARN of a lambda to run tasks after the test listener serves traffic to the replacement task set.
        :param after_allow_traffic: (experimental) Lambda or ARN of a lambda to run tasks after the second target group serves traffic to the replacement task set.
        :param after_install: (experimental) Lambda or ARN of a lambda to run tasks after the replacement task set is created and one of the target groups is associated with it.
        :param before_allow_traffic: (experimental) Lambda or ARN of a lambda to run tasks after the second target group is associated with the replacement task set, but before traffic is shifted to the replacement task set.
        :param before_install: (experimental) Lambda or ARN of a lambda to run tasks before the replacement task set is created.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87d5882f317f0c77b4b3020db23e892ee7831c1c15bdc09ffc0cd0be4c287bba)
            check_type(argname="argument after_allow_test_traffic", value=after_allow_test_traffic, expected_type=type_hints["after_allow_test_traffic"])
            check_type(argname="argument after_allow_traffic", value=after_allow_traffic, expected_type=type_hints["after_allow_traffic"])
            check_type(argname="argument after_install", value=after_install, expected_type=type_hints["after_install"])
            check_type(argname="argument before_allow_traffic", value=before_allow_traffic, expected_type=type_hints["before_allow_traffic"])
            check_type(argname="argument before_install", value=before_install, expected_type=type_hints["before_install"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if after_allow_test_traffic is not None:
            self._values["after_allow_test_traffic"] = after_allow_test_traffic
        if after_allow_traffic is not None:
            self._values["after_allow_traffic"] = after_allow_traffic
        if after_install is not None:
            self._values["after_install"] = after_install
        if before_allow_traffic is not None:
            self._values["before_allow_traffic"] = before_allow_traffic
        if before_install is not None:
            self._values["before_install"] = before_install

    @builtins.property
    def after_allow_test_traffic(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]]:
        '''(experimental) Lambda or ARN of a lambda to run tasks after the test listener serves traffic to the replacement task set.

        :stability: experimental
        '''
        result = self._values.get("after_allow_test_traffic")
        return typing.cast(typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]], result)

    @builtins.property
    def after_allow_traffic(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]]:
        '''(experimental) Lambda or ARN of a lambda to run tasks after the second target group serves traffic to the replacement task set.

        :stability: experimental
        '''
        result = self._values.get("after_allow_traffic")
        return typing.cast(typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]], result)

    @builtins.property
    def after_install(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]]:
        '''(experimental) Lambda or ARN of a lambda to run tasks after the replacement task set is created and one of the target groups is associated with it.

        :stability: experimental
        '''
        result = self._values.get("after_install")
        return typing.cast(typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]], result)

    @builtins.property
    def before_allow_traffic(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]]:
        '''(experimental) Lambda or ARN of a lambda to run tasks after the second target group is associated with the replacement task set, but before traffic is shifted to the replacement task set.

        :stability: experimental
        '''
        result = self._values.get("before_allow_traffic")
        return typing.cast(typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]], result)

    @builtins.property
    def before_install(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]]:
        '''(experimental) Lambda or ARN of a lambda to run tasks before the replacement task set is created.

        :stability: experimental
        '''
        result = self._values.get("before_install")
        return typing.cast(typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppSpecHooks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApplicationLoadBalancedCodeDeployedFargateService(
    _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedFargateService,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-ecs-codedeploy.ApplicationLoadBalancedCodeDeployedFargateService",
):
    '''(experimental) A Fargate service running on an ECS cluster fronted by an application load balancer and deployed by CodeDeploy.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        access_log_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        access_log_prefix: typing.Optional[builtins.str] = None,
        api_canary_schedule: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        api_canary_thread_count: typing.Optional[jsii.Number] = None,
        api_canary_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        api_test_steps: typing.Optional[typing.Sequence[typing.Union[ApiTestStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        application_name: typing.Optional[builtins.str] = None,
        deployment_config: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IEcsDeploymentConfig] = None,
        deployment_group_name: typing.Optional[builtins.str] = None,
        deployment_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        deregistration_delay: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        hooks: typing.Optional[typing.Union[AppSpecHooks, typing.Dict[builtins.str, typing.Any]]] = None,
        response_time_alarm_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        target_health_check: typing.Optional[typing.Union[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
        termination_wait_time: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        test_port: typing.Optional[jsii.Number] = None,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        task_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
        certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
        cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
        deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
        desired_count: typing.Optional[jsii.Number] = None,
        domain_name: typing.Optional[builtins.str] = None,
        domain_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        listener_port: typing.Optional[jsii.Number] = None,
        load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer] = None,
        load_balancer_name: typing.Optional[builtins.str] = None,
        max_healthy_percent: typing.Optional[jsii.Number] = None,
        min_healthy_percent: typing.Optional[jsii.Number] = None,
        open_listener: typing.Optional[builtins.bool] = None,
        propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
        public_load_balancer: typing.Optional[builtins.bool] = None,
        record_type: typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType] = None,
        redirect_http: typing.Optional[builtins.bool] = None,
        service_name: typing.Optional[builtins.str] = None,
        ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
        target_protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        task_image_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        cpu: typing.Optional[jsii.Number] = None,
        ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
        runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
        task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
    ) -> None:
        '''(experimental) Constructs a new instance of the ApplicationLoadBalancedCodeDeployedFargateService class.

        :param scope: -
        :param id: -
        :param access_log_bucket: (experimental) The bucket to use for access logs from the Application Load Balancer. Default: - a new S3 bucket will be created
        :param access_log_prefix: (experimental) The prefix to use for access logs from the Application Load Balancer. Default: - none
        :param api_canary_schedule: (experimental) The frequency for running the api canaries. Default: - 5 minutes
        :param api_canary_thread_count: (experimental) The number of threads to run concurrently for the synthetic test. Default: - 20
        :param api_canary_timeout: (experimental) The threshold for how long a api canary can take to run. Default: - no alarm is created for test duration
        :param api_test_steps: (experimental) The steps to run in the canary. Default: - no synthetic test will be created
        :param application_name: (experimental) The physical, human-readable name of the CodeDeploy Application. Default: an auto-generated name will be used
        :param deployment_config: (experimental) The deployment configuration to use for the deployment group. Default: - EcsDeploymentConfig.ALL_AT_ONCE
        :param deployment_group_name: (experimental) The physical, human-readable name of the CodeDeploy Deployment Group. Default: An auto-generated name will be used.
        :param deployment_timeout: (experimental) The timeout for a CodeDeploy deployment. Default: - 60 minutes
        :param deregistration_delay: (experimental) The amount of time for ELB to wait before changing the state of a deregistering target from 'draining' to 'unused'. Default: - 300 seconds
        :param hooks: (experimental) Optional lifecycle hooks. Default: - no lifecycle hooks
        :param response_time_alarm_threshold: (experimental) The threshold for response time alarm. Default: - no alarm will be created
        :param target_health_check: (experimental) The healthcheck to configure on the Application Load Balancer target groups. Default: - no health check is configured
        :param termination_wait_time: (experimental) The time to wait before terminating the original (blue) task set. Default: - 10 minutes
        :param test_port: (experimental) The port to use for test traffic on the listener. Default: - listenerPort + 1
        :param assign_public_ip: Determines whether the service will be assigned a public IP address. Default: false
        :param health_check: The health check command and associated configuration parameters for the container. Default: - Health check configuration from container.
        :param security_groups: The security groups to associate with the service. If you do not specify a security group, a new security group is created. Default: - A new security group is created.
        :param task_subnets: The subnets to associate with the service. Default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        :param capacity_provider_strategies: A list of Capacity Provider strategies used to place a service. Default: - undefined
        :param certificate: Certificate Manager certificate to associate with the load balancer. Setting this option will set the load balancer protocol to HTTPS. Default: - No certificate associated with the load balancer, if using the HTTP protocol. For HTTPS, a DNS-validated certificate will be created for the load balancer's specified domain name if a domain name and domain zone are specified.
        :param circuit_breaker: Whether to enable the deployment circuit breaker. If this property is defined, circuit breaker will be implicitly enabled. Default: - disabled
        :param cloud_map_options: The options for configuring an Amazon ECS service to use service discovery. Default: - AWS Cloud Map service discovery is not enabled.
        :param cluster: The name of the cluster that hosts the service. If a cluster is specified, the vpc construct should be omitted. Alternatively, you can omit both cluster and vpc. Default: - create a new cluster; if both cluster and vpc are omitted, a new VPC will be created for you.
        :param deployment_controller: Specifies which deployment controller to use for the service. For more information, see `Amazon ECS Deployment Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`_ Default: - Rolling update (ECS)
        :param desired_count: The desired number of instantiations of the task definition to keep running on the service. The minimum value is 1 Default: - The default is 1 for all new services and uses the existing service's desired count when updating an existing service.
        :param domain_name: The domain name for the service, e.g. "api.example.com.". Default: - No domain name.
        :param domain_zone: The Route53 hosted zone for the domain, e.g. "example.com.". Default: - No Route53 hosted domain zone.
        :param enable_ecs_managed_tags: Specifies whether to enable Amazon ECS managed tags for the tasks within the service. For more information, see `Tagging Your Amazon ECS Resources <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-using-tags.html>`_ Default: false
        :param enable_execute_command: Whether ECS Exec should be enabled. Default: - false
        :param health_check_grace_period: The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started. Default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        :param idle_timeout: The load balancer idle timeout, in seconds. Can be between 1 and 4000 seconds Default: - CloudFormation sets idle timeout to 60 seconds
        :param listener_port: Listener port of the application load balancer that will serve traffic to the service. Default: - The default listener port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). A domain name and zone must be also be specified if using HTTPS.
        :param load_balancer: The application load balancer that will serve traffic to the service. The VPC attribute of a load balancer must be specified for it to be used to create a new service with this pattern. [disable-awslint:ref-via-interface] Default: - a new load balancer will be created.
        :param load_balancer_name: Name of the load balancer. Default: - Automatically generated name.
        :param max_healthy_percent: The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment. Default: - 100 if daemon, otherwise 200
        :param min_healthy_percent: The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment. Default: - 0 if daemon, otherwise 50
        :param open_listener: Determines whether or not the Security Group for the Load Balancer's Listener will be open to all traffic by default. Default: true -- The security group allows ingress from all IP addresses.
        :param propagate_tags: Specifies whether to propagate the tags from the task definition or the service to the tasks in the service. Tags can only be propagated to the tasks within the service during service creation. Default: - none
        :param protocol: The protocol for connections from clients to the load balancer. The load balancer port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). If HTTPS, either a certificate or domain name and domain zone must also be specified. Default: HTTP. If a certificate is specified, the protocol will be set by default to HTTPS.
        :param protocol_version: The protocol version to use. Default: ApplicationProtocolVersion.HTTP1
        :param public_load_balancer: Determines whether the Load Balancer will be internet-facing. Default: true
        :param record_type: Specifies whether the Route53 record should be a CNAME, an A record using the Alias feature or no record at all. This is useful if you need to work with DNS systems that do not support alias records. Default: ApplicationLoadBalancedServiceRecordType.ALIAS
        :param redirect_http: Specifies whether the load balancer should redirect traffic on port 80 to port 443 to support HTTP->HTTPS redirects This is only valid if the protocol of the ALB is HTTPS. Default: false
        :param service_name: The name of the service. Default: - CloudFormation-generated name.
        :param ssl_policy: The security policy that defines which ciphers and protocols are supported by the ALB Listener. Default: - The recommended elastic load balancing security policy
        :param target_protocol: The protocol for connections from the load balancer to the ECS tasks. The default target port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). Default: HTTP.
        :param task_image_options: The properties required to create a new task definition. TaskDefinition or TaskImageOptions must be specified, but not both. Default: none
        :param vpc: The VPC where the container instances will be launched or the elastic network interfaces (ENIs) will be deployed. If a vpc is specified, the cluster construct should be omitted. Alternatively, you can omit both vpc and cluster. Default: - uses the VPC defined in the cluster or creates a new VPC.
        :param cpu: The number of cpu units used by the task. Valid values, which determines your range of valid values for the memory parameter: 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments 8192 (8 vCPU) - Available memory values: Between 16GB and 60GB in 4GB increments 16384 (16 vCPU) - Available memory values: Between 32GB and 120GB in 8GB increments This default is set in the underlying FargateTaskDefinition construct. Default: 256
        :param ephemeral_storage_gib: The amount (in GiB) of ephemeral storage to be allocated to the task. The minimum supported value is ``21`` GiB and the maximum supported value is ``200`` GiB. Only supported in Fargate platform version 1.4.0 or later. Default: Undefined, in which case, the task will receive 20GiB ephemeral storage.
        :param memory_limit_mib: The amount (in MiB) of memory used by the task. This field is required and you must use one of the following values, which determines your range of valid values for the cpu parameter: 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU) 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU) 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU) Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU) Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU) Between 16384 (16 GB) and 61440 (60 GB) in increments of 4096 (4 GB) - Available cpu values: 8192 (8 vCPU) Between 32768 (32 GB) and 122880 (120 GB) in increments of 8192 (8 GB) - Available cpu values: 16384 (16 vCPU) This default is set in the underlying FargateTaskDefinition construct. Default: 512
        :param platform_version: The platform version on which to run your service. If one is not specified, the LATEST platform version is used by default. For more information, see `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_ in the Amazon Elastic Container Service Developer Guide. Default: Latest
        :param runtime_platform: The runtime platform of the task definition. Default: - If the property is undefined, ``operatingSystemFamily`` is LINUX and ``cpuArchitecture`` is X86_64
        :param task_definition: The task definition to use for tasks in the service. TaskDefinition or TaskImageOptions must be specified, but not both. [disable-awslint:ref-via-interface] Default: - none

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6736d1d0b574dec7792a72d160022fb3d36b354822af032896dd4f37f5ca9b8f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ApplicationLoadBalancedCodeDeployedFargateServiceProps(
            access_log_bucket=access_log_bucket,
            access_log_prefix=access_log_prefix,
            api_canary_schedule=api_canary_schedule,
            api_canary_thread_count=api_canary_thread_count,
            api_canary_timeout=api_canary_timeout,
            api_test_steps=api_test_steps,
            application_name=application_name,
            deployment_config=deployment_config,
            deployment_group_name=deployment_group_name,
            deployment_timeout=deployment_timeout,
            deregistration_delay=deregistration_delay,
            hooks=hooks,
            response_time_alarm_threshold=response_time_alarm_threshold,
            target_health_check=target_health_check,
            termination_wait_time=termination_wait_time,
            test_port=test_port,
            assign_public_ip=assign_public_ip,
            health_check=health_check,
            security_groups=security_groups,
            task_subnets=task_subnets,
            capacity_provider_strategies=capacity_provider_strategies,
            certificate=certificate,
            circuit_breaker=circuit_breaker,
            cloud_map_options=cloud_map_options,
            cluster=cluster,
            deployment_controller=deployment_controller,
            desired_count=desired_count,
            domain_name=domain_name,
            domain_zone=domain_zone,
            enable_ecs_managed_tags=enable_ecs_managed_tags,
            enable_execute_command=enable_execute_command,
            health_check_grace_period=health_check_grace_period,
            idle_timeout=idle_timeout,
            listener_port=listener_port,
            load_balancer=load_balancer,
            load_balancer_name=load_balancer_name,
            max_healthy_percent=max_healthy_percent,
            min_healthy_percent=min_healthy_percent,
            open_listener=open_listener,
            propagate_tags=propagate_tags,
            protocol=protocol,
            protocol_version=protocol_version,
            public_load_balancer=public_load_balancer,
            record_type=record_type,
            redirect_http=redirect_http,
            service_name=service_name,
            ssl_policy=ssl_policy,
            target_protocol=target_protocol,
            task_image_options=task_image_options,
            vpc=vpc,
            cpu=cpu,
            ephemeral_storage_gib=ephemeral_storage_gib,
            memory_limit_mib=memory_limit_mib,
            platform_version=platform_version,
            runtime_platform=runtime_platform,
            task_definition=task_definition,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addServiceAsTarget")
    def _add_service_as_target(
        self,
        service: _aws_cdk_aws_ecs_ceddda9d.BaseService,
    ) -> None:
        '''(experimental) Adds service as a target of the target group.

        :param service: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c9be01440d9f934df9cd543843f7c6cedddf85074119c83a9dc135e7f624ad6)
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
        return typing.cast(None, jsii.invoke(self, "addServiceAsTarget", [service]))

    @builtins.property
    @jsii.member(jsii_name="accessLogBucket")
    def access_log_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''(experimental) S3 Bucket used for access logs.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "accessLogBucket"))

    @access_log_bucket.setter
    def access_log_bucket(self, value: _aws_cdk_aws_s3_ceddda9d.IBucket) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7447c7e10dcde2ca43c49add170830026b87ed7d494c7d26cfab83f894422f58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessLogBucket", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="application")
    def application(self) -> _aws_cdk_aws_codedeploy_ceddda9d.EcsApplication:
        '''(experimental) CodeDeploy application for this service.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_codedeploy_ceddda9d.EcsApplication, jsii.get(self, "application"))

    @application.setter
    def application(
        self,
        value: _aws_cdk_aws_codedeploy_ceddda9d.EcsApplication,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19f6fc9043e008683908ea78ba0046c1ab7547e85d051ddfc1c2fda80aaaa948)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "application", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deployment")
    def deployment(self) -> "EcsDeployment":
        '''(experimental) CodeDeploy deployment for this service.

        :stability: experimental
        '''
        return typing.cast("EcsDeployment", jsii.get(self, "deployment"))

    @deployment.setter
    def deployment(self, value: "EcsDeployment") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__311404106c32389cecdf74bfa60f61a4655e983615508a7acd9f4bd9b24ce958)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deployment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deploymentGroup")
    def deployment_group(self) -> _aws_cdk_aws_codedeploy_ceddda9d.EcsDeploymentGroup:
        '''(experimental) CodeDeploy deployment group for this service.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_codedeploy_ceddda9d.EcsDeploymentGroup, jsii.get(self, "deploymentGroup"))

    @deployment_group.setter
    def deployment_group(
        self,
        value: _aws_cdk_aws_codedeploy_ceddda9d.EcsDeploymentGroup,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ea1e4a8c09ecded833b997f80fb0e9df7eac4e09fd6bdfb81c0c3be8f653aad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deploymentGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="greenTargetGroup")
    def green_target_group(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationTargetGroup:
        '''(experimental) Test target group to use for CodeDeploy deployments.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationTargetGroup, jsii.get(self, "greenTargetGroup"))

    @green_target_group.setter
    def green_target_group(
        self,
        value: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationTargetGroup,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f4dbd3c75011f6cdb6230ceac17e417f8695b3dbbb5308e679013801a287934)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "greenTargetGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="testListener")
    def test_listener(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListener:
        '''(experimental) Test listener to use for CodeDeploy deployments.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListener, jsii.get(self, "testListener"))

    @test_listener.setter
    def test_listener(
        self,
        value: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListener,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__588edfc0c2963040dfc1d1d6d3818d3d4db18e61f20734f62776940b00eb5b88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "testListener", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="apiCanary")
    def api_canary(self) -> typing.Optional[ApiCanary]:
        '''(experimental) API Canary for the service.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[ApiCanary], jsii.get(self, "apiCanary"))

    @api_canary.setter
    def api_canary(self, value: typing.Optional[ApiCanary]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ccaa296e9a9496ff6b2bdf82b089f13e1d085ab5e7ae45642938930901923e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiCanary", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="healthAlarm")
    def health_alarm(self) -> typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]:
        '''(experimental) Composite alarm for monitoring health of service.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm], jsii.get(self, "healthAlarm"))

    @health_alarm.setter
    def health_alarm(
        self,
        value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d150c4633641ccb074c83db146501c42346deda1c4eec3ca8929f59d0523898)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "healthAlarm", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdklabs/cdk-ecs-codedeploy.ApplicationLoadBalancedCodeDeployedFargateServiceProps",
    jsii_struct_bases=[
        _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedFargateServiceProps
    ],
    name_mapping={
        "capacity_provider_strategies": "capacityProviderStrategies",
        "certificate": "certificate",
        "circuit_breaker": "circuitBreaker",
        "cloud_map_options": "cloudMapOptions",
        "cluster": "cluster",
        "deployment_controller": "deploymentController",
        "desired_count": "desiredCount",
        "domain_name": "domainName",
        "domain_zone": "domainZone",
        "enable_ecs_managed_tags": "enableECSManagedTags",
        "enable_execute_command": "enableExecuteCommand",
        "health_check_grace_period": "healthCheckGracePeriod",
        "idle_timeout": "idleTimeout",
        "listener_port": "listenerPort",
        "load_balancer": "loadBalancer",
        "load_balancer_name": "loadBalancerName",
        "max_healthy_percent": "maxHealthyPercent",
        "min_healthy_percent": "minHealthyPercent",
        "open_listener": "openListener",
        "propagate_tags": "propagateTags",
        "protocol": "protocol",
        "protocol_version": "protocolVersion",
        "public_load_balancer": "publicLoadBalancer",
        "record_type": "recordType",
        "redirect_http": "redirectHTTP",
        "service_name": "serviceName",
        "ssl_policy": "sslPolicy",
        "target_protocol": "targetProtocol",
        "task_image_options": "taskImageOptions",
        "vpc": "vpc",
        "cpu": "cpu",
        "ephemeral_storage_gib": "ephemeralStorageGiB",
        "memory_limit_mib": "memoryLimitMiB",
        "platform_version": "platformVersion",
        "runtime_platform": "runtimePlatform",
        "task_definition": "taskDefinition",
        "assign_public_ip": "assignPublicIp",
        "health_check": "healthCheck",
        "security_groups": "securityGroups",
        "task_subnets": "taskSubnets",
        "access_log_bucket": "accessLogBucket",
        "access_log_prefix": "accessLogPrefix",
        "api_canary_schedule": "apiCanarySchedule",
        "api_canary_thread_count": "apiCanaryThreadCount",
        "api_canary_timeout": "apiCanaryTimeout",
        "api_test_steps": "apiTestSteps",
        "application_name": "applicationName",
        "deployment_config": "deploymentConfig",
        "deployment_group_name": "deploymentGroupName",
        "deployment_timeout": "deploymentTimeout",
        "deregistration_delay": "deregistrationDelay",
        "hooks": "hooks",
        "response_time_alarm_threshold": "responseTimeAlarmThreshold",
        "target_health_check": "targetHealthCheck",
        "termination_wait_time": "terminationWaitTime",
        "test_port": "testPort",
    },
)
class ApplicationLoadBalancedCodeDeployedFargateServiceProps(
    _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedFargateServiceProps,
):
    def __init__(
        self,
        *,
        capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
        certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
        circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
        cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
        deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
        desired_count: typing.Optional[jsii.Number] = None,
        domain_name: typing.Optional[builtins.str] = None,
        domain_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
        enable_execute_command: typing.Optional[builtins.bool] = None,
        health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        listener_port: typing.Optional[jsii.Number] = None,
        load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer] = None,
        load_balancer_name: typing.Optional[builtins.str] = None,
        max_healthy_percent: typing.Optional[jsii.Number] = None,
        min_healthy_percent: typing.Optional[jsii.Number] = None,
        open_listener: typing.Optional[builtins.bool] = None,
        propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
        protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
        public_load_balancer: typing.Optional[builtins.bool] = None,
        record_type: typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType] = None,
        redirect_http: typing.Optional[builtins.bool] = None,
        service_name: typing.Optional[builtins.str] = None,
        ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
        target_protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
        task_image_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        cpu: typing.Optional[jsii.Number] = None,
        ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
        runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
        task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        task_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        access_log_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        access_log_prefix: typing.Optional[builtins.str] = None,
        api_canary_schedule: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        api_canary_thread_count: typing.Optional[jsii.Number] = None,
        api_canary_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        api_test_steps: typing.Optional[typing.Sequence[typing.Union[ApiTestStep, typing.Dict[builtins.str, typing.Any]]]] = None,
        application_name: typing.Optional[builtins.str] = None,
        deployment_config: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IEcsDeploymentConfig] = None,
        deployment_group_name: typing.Optional[builtins.str] = None,
        deployment_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        deregistration_delay: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        hooks: typing.Optional[typing.Union[AppSpecHooks, typing.Dict[builtins.str, typing.Any]]] = None,
        response_time_alarm_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        target_health_check: typing.Optional[typing.Union[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
        termination_wait_time: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        test_port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) The properties for the ApplicationLoadBalancedCodeDeployedFargateService service.

        :param capacity_provider_strategies: A list of Capacity Provider strategies used to place a service. Default: - undefined
        :param certificate: Certificate Manager certificate to associate with the load balancer. Setting this option will set the load balancer protocol to HTTPS. Default: - No certificate associated with the load balancer, if using the HTTP protocol. For HTTPS, a DNS-validated certificate will be created for the load balancer's specified domain name if a domain name and domain zone are specified.
        :param circuit_breaker: Whether to enable the deployment circuit breaker. If this property is defined, circuit breaker will be implicitly enabled. Default: - disabled
        :param cloud_map_options: The options for configuring an Amazon ECS service to use service discovery. Default: - AWS Cloud Map service discovery is not enabled.
        :param cluster: The name of the cluster that hosts the service. If a cluster is specified, the vpc construct should be omitted. Alternatively, you can omit both cluster and vpc. Default: - create a new cluster; if both cluster and vpc are omitted, a new VPC will be created for you.
        :param deployment_controller: Specifies which deployment controller to use for the service. For more information, see `Amazon ECS Deployment Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`_ Default: - Rolling update (ECS)
        :param desired_count: The desired number of instantiations of the task definition to keep running on the service. The minimum value is 1 Default: - The default is 1 for all new services and uses the existing service's desired count when updating an existing service.
        :param domain_name: The domain name for the service, e.g. "api.example.com.". Default: - No domain name.
        :param domain_zone: The Route53 hosted zone for the domain, e.g. "example.com.". Default: - No Route53 hosted domain zone.
        :param enable_ecs_managed_tags: Specifies whether to enable Amazon ECS managed tags for the tasks within the service. For more information, see `Tagging Your Amazon ECS Resources <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-using-tags.html>`_ Default: false
        :param enable_execute_command: Whether ECS Exec should be enabled. Default: - false
        :param health_check_grace_period: The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started. Default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        :param idle_timeout: The load balancer idle timeout, in seconds. Can be between 1 and 4000 seconds Default: - CloudFormation sets idle timeout to 60 seconds
        :param listener_port: Listener port of the application load balancer that will serve traffic to the service. Default: - The default listener port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). A domain name and zone must be also be specified if using HTTPS.
        :param load_balancer: The application load balancer that will serve traffic to the service. The VPC attribute of a load balancer must be specified for it to be used to create a new service with this pattern. [disable-awslint:ref-via-interface] Default: - a new load balancer will be created.
        :param load_balancer_name: Name of the load balancer. Default: - Automatically generated name.
        :param max_healthy_percent: The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment. Default: - 100 if daemon, otherwise 200
        :param min_healthy_percent: The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment. Default: - 0 if daemon, otherwise 50
        :param open_listener: Determines whether or not the Security Group for the Load Balancer's Listener will be open to all traffic by default. Default: true -- The security group allows ingress from all IP addresses.
        :param propagate_tags: Specifies whether to propagate the tags from the task definition or the service to the tasks in the service. Tags can only be propagated to the tasks within the service during service creation. Default: - none
        :param protocol: The protocol for connections from clients to the load balancer. The load balancer port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). If HTTPS, either a certificate or domain name and domain zone must also be specified. Default: HTTP. If a certificate is specified, the protocol will be set by default to HTTPS.
        :param protocol_version: The protocol version to use. Default: ApplicationProtocolVersion.HTTP1
        :param public_load_balancer: Determines whether the Load Balancer will be internet-facing. Default: true
        :param record_type: Specifies whether the Route53 record should be a CNAME, an A record using the Alias feature or no record at all. This is useful if you need to work with DNS systems that do not support alias records. Default: ApplicationLoadBalancedServiceRecordType.ALIAS
        :param redirect_http: Specifies whether the load balancer should redirect traffic on port 80 to port 443 to support HTTP->HTTPS redirects This is only valid if the protocol of the ALB is HTTPS. Default: false
        :param service_name: The name of the service. Default: - CloudFormation-generated name.
        :param ssl_policy: The security policy that defines which ciphers and protocols are supported by the ALB Listener. Default: - The recommended elastic load balancing security policy
        :param target_protocol: The protocol for connections from the load balancer to the ECS tasks. The default target port is determined from the protocol (port 80 for HTTP, port 443 for HTTPS). Default: HTTP.
        :param task_image_options: The properties required to create a new task definition. TaskDefinition or TaskImageOptions must be specified, but not both. Default: none
        :param vpc: The VPC where the container instances will be launched or the elastic network interfaces (ENIs) will be deployed. If a vpc is specified, the cluster construct should be omitted. Alternatively, you can omit both vpc and cluster. Default: - uses the VPC defined in the cluster or creates a new VPC.
        :param cpu: The number of cpu units used by the task. Valid values, which determines your range of valid values for the memory parameter: 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments 8192 (8 vCPU) - Available memory values: Between 16GB and 60GB in 4GB increments 16384 (16 vCPU) - Available memory values: Between 32GB and 120GB in 8GB increments This default is set in the underlying FargateTaskDefinition construct. Default: 256
        :param ephemeral_storage_gib: The amount (in GiB) of ephemeral storage to be allocated to the task. The minimum supported value is ``21`` GiB and the maximum supported value is ``200`` GiB. Only supported in Fargate platform version 1.4.0 or later. Default: Undefined, in which case, the task will receive 20GiB ephemeral storage.
        :param memory_limit_mib: The amount (in MiB) of memory used by the task. This field is required and you must use one of the following values, which determines your range of valid values for the cpu parameter: 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU) 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU) 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU) Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU) Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU) Between 16384 (16 GB) and 61440 (60 GB) in increments of 4096 (4 GB) - Available cpu values: 8192 (8 vCPU) Between 32768 (32 GB) and 122880 (120 GB) in increments of 8192 (8 GB) - Available cpu values: 16384 (16 vCPU) This default is set in the underlying FargateTaskDefinition construct. Default: 512
        :param platform_version: The platform version on which to run your service. If one is not specified, the LATEST platform version is used by default. For more information, see `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_ in the Amazon Elastic Container Service Developer Guide. Default: Latest
        :param runtime_platform: The runtime platform of the task definition. Default: - If the property is undefined, ``operatingSystemFamily`` is LINUX and ``cpuArchitecture`` is X86_64
        :param task_definition: The task definition to use for tasks in the service. TaskDefinition or TaskImageOptions must be specified, but not both. [disable-awslint:ref-via-interface] Default: - none
        :param assign_public_ip: Determines whether the service will be assigned a public IP address. Default: false
        :param health_check: The health check command and associated configuration parameters for the container. Default: - Health check configuration from container.
        :param security_groups: The security groups to associate with the service. If you do not specify a security group, a new security group is created. Default: - A new security group is created.
        :param task_subnets: The subnets to associate with the service. Default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        :param access_log_bucket: (experimental) The bucket to use for access logs from the Application Load Balancer. Default: - a new S3 bucket will be created
        :param access_log_prefix: (experimental) The prefix to use for access logs from the Application Load Balancer. Default: - none
        :param api_canary_schedule: (experimental) The frequency for running the api canaries. Default: - 5 minutes
        :param api_canary_thread_count: (experimental) The number of threads to run concurrently for the synthetic test. Default: - 20
        :param api_canary_timeout: (experimental) The threshold for how long a api canary can take to run. Default: - no alarm is created for test duration
        :param api_test_steps: (experimental) The steps to run in the canary. Default: - no synthetic test will be created
        :param application_name: (experimental) The physical, human-readable name of the CodeDeploy Application. Default: an auto-generated name will be used
        :param deployment_config: (experimental) The deployment configuration to use for the deployment group. Default: - EcsDeploymentConfig.ALL_AT_ONCE
        :param deployment_group_name: (experimental) The physical, human-readable name of the CodeDeploy Deployment Group. Default: An auto-generated name will be used.
        :param deployment_timeout: (experimental) The timeout for a CodeDeploy deployment. Default: - 60 minutes
        :param deregistration_delay: (experimental) The amount of time for ELB to wait before changing the state of a deregistering target from 'draining' to 'unused'. Default: - 300 seconds
        :param hooks: (experimental) Optional lifecycle hooks. Default: - no lifecycle hooks
        :param response_time_alarm_threshold: (experimental) The threshold for response time alarm. Default: - no alarm will be created
        :param target_health_check: (experimental) The healthcheck to configure on the Application Load Balancer target groups. Default: - no health check is configured
        :param termination_wait_time: (experimental) The time to wait before terminating the original (blue) task set. Default: - 10 minutes
        :param test_port: (experimental) The port to use for test traffic on the listener. Default: - listenerPort + 1

        :stability: experimental
        '''
        if isinstance(circuit_breaker, dict):
            circuit_breaker = _aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker(**circuit_breaker)
        if isinstance(cloud_map_options, dict):
            cloud_map_options = _aws_cdk_aws_ecs_ceddda9d.CloudMapOptions(**cloud_map_options)
        if isinstance(deployment_controller, dict):
            deployment_controller = _aws_cdk_aws_ecs_ceddda9d.DeploymentController(**deployment_controller)
        if isinstance(task_image_options, dict):
            task_image_options = _aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions(**task_image_options)
        if isinstance(runtime_platform, dict):
            runtime_platform = _aws_cdk_aws_ecs_ceddda9d.RuntimePlatform(**runtime_platform)
        if isinstance(health_check, dict):
            health_check = _aws_cdk_aws_ecs_ceddda9d.HealthCheck(**health_check)
        if isinstance(task_subnets, dict):
            task_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**task_subnets)
        if isinstance(hooks, dict):
            hooks = AppSpecHooks(**hooks)
        if isinstance(target_health_check, dict):
            target_health_check = _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck(**target_health_check)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27c0c490ffab55452beb7a0943b27b71229ff007f255832d362d9af91fbe01b9)
            check_type(argname="argument capacity_provider_strategies", value=capacity_provider_strategies, expected_type=type_hints["capacity_provider_strategies"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument circuit_breaker", value=circuit_breaker, expected_type=type_hints["circuit_breaker"])
            check_type(argname="argument cloud_map_options", value=cloud_map_options, expected_type=type_hints["cloud_map_options"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument deployment_controller", value=deployment_controller, expected_type=type_hints["deployment_controller"])
            check_type(argname="argument desired_count", value=desired_count, expected_type=type_hints["desired_count"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument domain_zone", value=domain_zone, expected_type=type_hints["domain_zone"])
            check_type(argname="argument enable_ecs_managed_tags", value=enable_ecs_managed_tags, expected_type=type_hints["enable_ecs_managed_tags"])
            check_type(argname="argument enable_execute_command", value=enable_execute_command, expected_type=type_hints["enable_execute_command"])
            check_type(argname="argument health_check_grace_period", value=health_check_grace_period, expected_type=type_hints["health_check_grace_period"])
            check_type(argname="argument idle_timeout", value=idle_timeout, expected_type=type_hints["idle_timeout"])
            check_type(argname="argument listener_port", value=listener_port, expected_type=type_hints["listener_port"])
            check_type(argname="argument load_balancer", value=load_balancer, expected_type=type_hints["load_balancer"])
            check_type(argname="argument load_balancer_name", value=load_balancer_name, expected_type=type_hints["load_balancer_name"])
            check_type(argname="argument max_healthy_percent", value=max_healthy_percent, expected_type=type_hints["max_healthy_percent"])
            check_type(argname="argument min_healthy_percent", value=min_healthy_percent, expected_type=type_hints["min_healthy_percent"])
            check_type(argname="argument open_listener", value=open_listener, expected_type=type_hints["open_listener"])
            check_type(argname="argument propagate_tags", value=propagate_tags, expected_type=type_hints["propagate_tags"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument protocol_version", value=protocol_version, expected_type=type_hints["protocol_version"])
            check_type(argname="argument public_load_balancer", value=public_load_balancer, expected_type=type_hints["public_load_balancer"])
            check_type(argname="argument record_type", value=record_type, expected_type=type_hints["record_type"])
            check_type(argname="argument redirect_http", value=redirect_http, expected_type=type_hints["redirect_http"])
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument ssl_policy", value=ssl_policy, expected_type=type_hints["ssl_policy"])
            check_type(argname="argument target_protocol", value=target_protocol, expected_type=type_hints["target_protocol"])
            check_type(argname="argument task_image_options", value=task_image_options, expected_type=type_hints["task_image_options"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument cpu", value=cpu, expected_type=type_hints["cpu"])
            check_type(argname="argument ephemeral_storage_gib", value=ephemeral_storage_gib, expected_type=type_hints["ephemeral_storage_gib"])
            check_type(argname="argument memory_limit_mib", value=memory_limit_mib, expected_type=type_hints["memory_limit_mib"])
            check_type(argname="argument platform_version", value=platform_version, expected_type=type_hints["platform_version"])
            check_type(argname="argument runtime_platform", value=runtime_platform, expected_type=type_hints["runtime_platform"])
            check_type(argname="argument task_definition", value=task_definition, expected_type=type_hints["task_definition"])
            check_type(argname="argument assign_public_ip", value=assign_public_ip, expected_type=type_hints["assign_public_ip"])
            check_type(argname="argument health_check", value=health_check, expected_type=type_hints["health_check"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument task_subnets", value=task_subnets, expected_type=type_hints["task_subnets"])
            check_type(argname="argument access_log_bucket", value=access_log_bucket, expected_type=type_hints["access_log_bucket"])
            check_type(argname="argument access_log_prefix", value=access_log_prefix, expected_type=type_hints["access_log_prefix"])
            check_type(argname="argument api_canary_schedule", value=api_canary_schedule, expected_type=type_hints["api_canary_schedule"])
            check_type(argname="argument api_canary_thread_count", value=api_canary_thread_count, expected_type=type_hints["api_canary_thread_count"])
            check_type(argname="argument api_canary_timeout", value=api_canary_timeout, expected_type=type_hints["api_canary_timeout"])
            check_type(argname="argument api_test_steps", value=api_test_steps, expected_type=type_hints["api_test_steps"])
            check_type(argname="argument application_name", value=application_name, expected_type=type_hints["application_name"])
            check_type(argname="argument deployment_config", value=deployment_config, expected_type=type_hints["deployment_config"])
            check_type(argname="argument deployment_group_name", value=deployment_group_name, expected_type=type_hints["deployment_group_name"])
            check_type(argname="argument deployment_timeout", value=deployment_timeout, expected_type=type_hints["deployment_timeout"])
            check_type(argname="argument deregistration_delay", value=deregistration_delay, expected_type=type_hints["deregistration_delay"])
            check_type(argname="argument hooks", value=hooks, expected_type=type_hints["hooks"])
            check_type(argname="argument response_time_alarm_threshold", value=response_time_alarm_threshold, expected_type=type_hints["response_time_alarm_threshold"])
            check_type(argname="argument target_health_check", value=target_health_check, expected_type=type_hints["target_health_check"])
            check_type(argname="argument termination_wait_time", value=termination_wait_time, expected_type=type_hints["termination_wait_time"])
            check_type(argname="argument test_port", value=test_port, expected_type=type_hints["test_port"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if capacity_provider_strategies is not None:
            self._values["capacity_provider_strategies"] = capacity_provider_strategies
        if certificate is not None:
            self._values["certificate"] = certificate
        if circuit_breaker is not None:
            self._values["circuit_breaker"] = circuit_breaker
        if cloud_map_options is not None:
            self._values["cloud_map_options"] = cloud_map_options
        if cluster is not None:
            self._values["cluster"] = cluster
        if deployment_controller is not None:
            self._values["deployment_controller"] = deployment_controller
        if desired_count is not None:
            self._values["desired_count"] = desired_count
        if domain_name is not None:
            self._values["domain_name"] = domain_name
        if domain_zone is not None:
            self._values["domain_zone"] = domain_zone
        if enable_ecs_managed_tags is not None:
            self._values["enable_ecs_managed_tags"] = enable_ecs_managed_tags
        if enable_execute_command is not None:
            self._values["enable_execute_command"] = enable_execute_command
        if health_check_grace_period is not None:
            self._values["health_check_grace_period"] = health_check_grace_period
        if idle_timeout is not None:
            self._values["idle_timeout"] = idle_timeout
        if listener_port is not None:
            self._values["listener_port"] = listener_port
        if load_balancer is not None:
            self._values["load_balancer"] = load_balancer
        if load_balancer_name is not None:
            self._values["load_balancer_name"] = load_balancer_name
        if max_healthy_percent is not None:
            self._values["max_healthy_percent"] = max_healthy_percent
        if min_healthy_percent is not None:
            self._values["min_healthy_percent"] = min_healthy_percent
        if open_listener is not None:
            self._values["open_listener"] = open_listener
        if propagate_tags is not None:
            self._values["propagate_tags"] = propagate_tags
        if protocol is not None:
            self._values["protocol"] = protocol
        if protocol_version is not None:
            self._values["protocol_version"] = protocol_version
        if public_load_balancer is not None:
            self._values["public_load_balancer"] = public_load_balancer
        if record_type is not None:
            self._values["record_type"] = record_type
        if redirect_http is not None:
            self._values["redirect_http"] = redirect_http
        if service_name is not None:
            self._values["service_name"] = service_name
        if ssl_policy is not None:
            self._values["ssl_policy"] = ssl_policy
        if target_protocol is not None:
            self._values["target_protocol"] = target_protocol
        if task_image_options is not None:
            self._values["task_image_options"] = task_image_options
        if vpc is not None:
            self._values["vpc"] = vpc
        if cpu is not None:
            self._values["cpu"] = cpu
        if ephemeral_storage_gib is not None:
            self._values["ephemeral_storage_gib"] = ephemeral_storage_gib
        if memory_limit_mib is not None:
            self._values["memory_limit_mib"] = memory_limit_mib
        if platform_version is not None:
            self._values["platform_version"] = platform_version
        if runtime_platform is not None:
            self._values["runtime_platform"] = runtime_platform
        if task_definition is not None:
            self._values["task_definition"] = task_definition
        if assign_public_ip is not None:
            self._values["assign_public_ip"] = assign_public_ip
        if health_check is not None:
            self._values["health_check"] = health_check
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if task_subnets is not None:
            self._values["task_subnets"] = task_subnets
        if access_log_bucket is not None:
            self._values["access_log_bucket"] = access_log_bucket
        if access_log_prefix is not None:
            self._values["access_log_prefix"] = access_log_prefix
        if api_canary_schedule is not None:
            self._values["api_canary_schedule"] = api_canary_schedule
        if api_canary_thread_count is not None:
            self._values["api_canary_thread_count"] = api_canary_thread_count
        if api_canary_timeout is not None:
            self._values["api_canary_timeout"] = api_canary_timeout
        if api_test_steps is not None:
            self._values["api_test_steps"] = api_test_steps
        if application_name is not None:
            self._values["application_name"] = application_name
        if deployment_config is not None:
            self._values["deployment_config"] = deployment_config
        if deployment_group_name is not None:
            self._values["deployment_group_name"] = deployment_group_name
        if deployment_timeout is not None:
            self._values["deployment_timeout"] = deployment_timeout
        if deregistration_delay is not None:
            self._values["deregistration_delay"] = deregistration_delay
        if hooks is not None:
            self._values["hooks"] = hooks
        if response_time_alarm_threshold is not None:
            self._values["response_time_alarm_threshold"] = response_time_alarm_threshold
        if target_health_check is not None:
            self._values["target_health_check"] = target_health_check
        if termination_wait_time is not None:
            self._values["termination_wait_time"] = termination_wait_time
        if test_port is not None:
            self._values["test_port"] = test_port

    @builtins.property
    def capacity_provider_strategies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy]]:
        '''A list of Capacity Provider strategies used to place a service.

        :default: - undefined
        '''
        result = self._values.get("capacity_provider_strategies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy]], result)

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        '''Certificate Manager certificate to associate with the load balancer.

        Setting this option will set the load balancer protocol to HTTPS.

        :default:

        - No certificate associated with the load balancer, if using
        the HTTP protocol. For HTTPS, a DNS-validated certificate will be
        created for the load balancer's specified domain name if a domain name
        and domain zone are specified.
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], result)

    @builtins.property
    def circuit_breaker(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker]:
        '''Whether to enable the deployment circuit breaker.

        If this property is defined, circuit breaker will be implicitly
        enabled.

        :default: - disabled
        '''
        result = self._values.get("circuit_breaker")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker], result)

    @builtins.property
    def cloud_map_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions]:
        '''The options for configuring an Amazon ECS service to use service discovery.

        :default: - AWS Cloud Map service discovery is not enabled.
        '''
        result = self._values.get("cloud_map_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions], result)

    @builtins.property
    def cluster(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster]:
        '''The name of the cluster that hosts the service.

        If a cluster is specified, the vpc construct should be omitted. Alternatively, you can omit both cluster and vpc.

        :default: - create a new cluster; if both cluster and vpc are omitted, a new VPC will be created for you.
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster], result)

    @builtins.property
    def deployment_controller(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentController]:
        '''Specifies which deployment controller to use for the service.

        For more information, see
        `Amazon ECS Deployment Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`_

        :default: - Rolling update (ECS)
        '''
        result = self._values.get("deployment_controller")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.DeploymentController], result)

    @builtins.property
    def desired_count(self) -> typing.Optional[jsii.Number]:
        '''The desired number of instantiations of the task definition to keep running on the service.

        The minimum value is 1

        :default:

        - The default is 1 for all new services and uses the existing service's desired count
        when updating an existing service.
        '''
        result = self._values.get("desired_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''The domain name for the service, e.g. "api.example.com.".

        :default: - No domain name.
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_zone(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone]:
        '''The Route53 hosted zone for the domain, e.g. "example.com.".

        :default: - No Route53 hosted domain zone.
        '''
        result = self._values.get("domain_zone")
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone], result)

    @builtins.property
    def enable_ecs_managed_tags(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether to enable Amazon ECS managed tags for the tasks within the service.

        For more information, see
        `Tagging Your Amazon ECS Resources <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-using-tags.html>`_

        :default: false
        '''
        result = self._values.get("enable_ecs_managed_tags")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_execute_command(self) -> typing.Optional[builtins.bool]:
        '''Whether ECS Exec should be enabled.

        :default: - false
        '''
        result = self._values.get("enable_execute_command")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def health_check_grace_period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started.

        :default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        '''
        result = self._values.get("health_check_grace_period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def idle_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The load balancer idle timeout, in seconds.

        Can be between 1 and 4000 seconds

        :default: - CloudFormation sets idle timeout to 60 seconds
        '''
        result = self._values.get("idle_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def listener_port(self) -> typing.Optional[jsii.Number]:
        '''Listener port of the application load balancer that will serve traffic to the service.

        :default:

        - The default listener port is determined from the protocol (port 80 for HTTP,
        port 443 for HTTPS). A domain name and zone must be also be specified if using HTTPS.
        '''
        result = self._values.get("listener_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def load_balancer(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer]:
        '''The application load balancer that will serve traffic to the service.

        The VPC attribute of a load balancer must be specified for it to be used
        to create a new service with this pattern.

        [disable-awslint:ref-via-interface]

        :default: - a new load balancer will be created.
        '''
        result = self._values.get("load_balancer")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer], result)

    @builtins.property
    def load_balancer_name(self) -> typing.Optional[builtins.str]:
        '''Name of the load balancer.

        :default: - Automatically generated name.
        '''
        result = self._values.get("load_balancer_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_healthy_percent(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment.

        :default: - 100 if daemon, otherwise 200
        '''
        result = self._values.get("max_healthy_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_healthy_percent(self) -> typing.Optional[jsii.Number]:
        '''The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment.

        :default: - 0 if daemon, otherwise 50
        '''
        result = self._values.get("min_healthy_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def open_listener(self) -> typing.Optional[builtins.bool]:
        '''Determines whether or not the Security Group for the Load Balancer's Listener will be open to all traffic by default.

        :default: true -- The security group allows ingress from all IP addresses.
        '''
        result = self._values.get("open_listener")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def propagate_tags(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource]:
        '''Specifies whether to propagate the tags from the task definition or the service to the tasks in the service.

        Tags can only be propagated to the tasks within the service during service creation.

        :default: - none
        '''
        result = self._values.get("propagate_tags")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource], result)

    @builtins.property
    def protocol(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol]:
        '''The protocol for connections from clients to the load balancer.

        The load balancer port is determined from the protocol (port 80 for
        HTTP, port 443 for HTTPS).  If HTTPS, either a certificate or domain
        name and domain zone must also be specified.

        :default:

        HTTP. If a certificate is specified, the protocol will be
        set by default to HTTPS.
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol], result)

    @builtins.property
    def protocol_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion]:
        '''The protocol version to use.

        :default: ApplicationProtocolVersion.HTTP1
        '''
        result = self._values.get("protocol_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion], result)

    @builtins.property
    def public_load_balancer(self) -> typing.Optional[builtins.bool]:
        '''Determines whether the Load Balancer will be internet-facing.

        :default: true
        '''
        result = self._values.get("public_load_balancer")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def record_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType]:
        '''Specifies whether the Route53 record should be a CNAME, an A record using the Alias feature or no record at all.

        This is useful if you need to work with DNS systems that do not support alias records.

        :default: ApplicationLoadBalancedServiceRecordType.ALIAS
        '''
        result = self._values.get("record_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType], result)

    @builtins.property
    def redirect_http(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether the load balancer should redirect traffic on port 80 to port 443 to support HTTP->HTTPS redirects This is only valid if the protocol of the ALB is HTTPS.

        :default: false
        '''
        result = self._values.get("redirect_http")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def service_name(self) -> typing.Optional[builtins.str]:
        '''The name of the service.

        :default: - CloudFormation-generated name.
        '''
        result = self._values.get("service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssl_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy]:
        '''The security policy that defines which ciphers and protocols are supported by the ALB Listener.

        :default: - The recommended elastic load balancing security policy
        '''
        result = self._values.get("ssl_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy], result)

    @builtins.property
    def target_protocol(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol]:
        '''The protocol for connections from the load balancer to the ECS tasks.

        The default target port is determined from the protocol (port 80 for
        HTTP, port 443 for HTTPS).

        :default: HTTP.
        '''
        result = self._values.get("target_protocol")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol], result)

    @builtins.property
    def task_image_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions]:
        '''The properties required to create a new task definition.

        TaskDefinition or TaskImageOptions must be specified, but not both.

        :default: none
        '''
        result = self._values.get("task_image_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''The VPC where the container instances will be launched or the elastic network interfaces (ENIs) will be deployed.

        If a vpc is specified, the cluster construct should be omitted. Alternatively, you can omit both vpc and cluster.

        :default: - uses the VPC defined in the cluster or creates a new VPC.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def cpu(self) -> typing.Optional[jsii.Number]:
        '''The number of cpu units used by the task.

        Valid values, which determines your range of valid values for the memory parameter:

        256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB

        512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB

        1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB

        2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments

        4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments

        8192 (8 vCPU) - Available memory values: Between 16GB and 60GB in 4GB increments

        16384 (16 vCPU) - Available memory values: Between 32GB and 120GB in 8GB increments

        This default is set in the underlying FargateTaskDefinition construct.

        :default: 256
        '''
        result = self._values.get("cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ephemeral_storage_gib(self) -> typing.Optional[jsii.Number]:
        '''The amount (in GiB) of ephemeral storage to be allocated to the task.

        The minimum supported value is ``21`` GiB and the maximum supported value is ``200`` GiB.

        Only supported in Fargate platform version 1.4.0 or later.

        :default: Undefined, in which case, the task will receive 20GiB ephemeral storage.
        '''
        result = self._values.get("ephemeral_storage_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_limit_mib(self) -> typing.Optional[jsii.Number]:
        '''The amount (in MiB) of memory used by the task.

        This field is required and you must use one of the following values, which determines your range of valid values
        for the cpu parameter:

        512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU)

        1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU)

        2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU)

        Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU)

        Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU)

        Between 16384 (16 GB) and 61440 (60 GB) in increments of 4096 (4 GB) - Available cpu values: 8192 (8 vCPU)

        Between 32768 (32 GB) and 122880 (120 GB) in increments of 8192 (8 GB) - Available cpu values: 16384 (16 vCPU)

        This default is set in the underlying FargateTaskDefinition construct.

        :default: 512
        '''
        result = self._values.get("memory_limit_mib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def platform_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion]:
        '''The platform version on which to run your service.

        If one is not specified, the LATEST platform version is used by default. For more information, see
        `AWS Fargate Platform Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`_
        in the Amazon Elastic Container Service Developer Guide.

        :default: Latest
        '''
        result = self._values.get("platform_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion], result)

    @builtins.property
    def runtime_platform(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform]:
        '''The runtime platform of the task definition.

        :default: - If the property is undefined, ``operatingSystemFamily`` is LINUX and ``cpuArchitecture`` is X86_64
        '''
        result = self._values.get("runtime_platform")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform], result)

    @builtins.property
    def task_definition(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition]:
        '''The task definition to use for tasks in the service. TaskDefinition or TaskImageOptions must be specified, but not both.

        [disable-awslint:ref-via-interface]

        :default: - none
        '''
        result = self._values.get("task_definition")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition], result)

    @builtins.property
    def assign_public_ip(self) -> typing.Optional[builtins.bool]:
        '''Determines whether the service will be assigned a public IP address.

        :default: false
        '''
        result = self._values.get("assign_public_ip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def health_check(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.HealthCheck]:
        '''The health check command and associated configuration parameters for the container.

        :default: - Health check configuration from container.
        '''
        result = self._values.get("health_check")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.HealthCheck], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The security groups to associate with the service.

        If you do not specify a security group, a new security group is created.

        :default: - A new security group is created.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def task_subnets(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''The subnets to associate with the service.

        :default: - Public subnets if ``assignPublicIp`` is set, otherwise the first available one of Private, Isolated, Public, in that order.
        '''
        result = self._values.get("task_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def access_log_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''(experimental) The bucket to use for access logs from the Application Load Balancer.

        :default: - a new S3 bucket will be created

        :stability: experimental
        '''
        result = self._values.get("access_log_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def access_log_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) The prefix to use for access logs from the Application Load Balancer.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("access_log_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_canary_schedule(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The frequency for running the api canaries.

        :default: - 5 minutes

        :stability: experimental
        '''
        result = self._values.get("api_canary_schedule")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def api_canary_thread_count(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of threads to run concurrently for the synthetic test.

        :default: - 20

        :stability: experimental
        '''
        result = self._values.get("api_canary_thread_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def api_canary_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The threshold for how long a api canary can take to run.

        :default: - no alarm is created for test duration

        :stability: experimental
        '''
        result = self._values.get("api_canary_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def api_test_steps(self) -> typing.Optional[typing.List[ApiTestStep]]:
        '''(experimental) The steps to run in the canary.

        :default: - no synthetic test will be created

        :stability: experimental
        '''
        result = self._values.get("api_test_steps")
        return typing.cast(typing.Optional[typing.List[ApiTestStep]], result)

    @builtins.property
    def application_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The physical, human-readable name of the CodeDeploy Application.

        :default: an auto-generated name will be used

        :stability: experimental
        '''
        result = self._values.get("application_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deployment_config(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IEcsDeploymentConfig]:
        '''(experimental) The deployment configuration to use for the deployment group.

        :default: - EcsDeploymentConfig.ALL_AT_ONCE

        :stability: experimental
        '''
        result = self._values.get("deployment_config")
        return typing.cast(typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IEcsDeploymentConfig], result)

    @builtins.property
    def deployment_group_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The physical, human-readable name of the CodeDeploy Deployment Group.

        :default: An auto-generated name will be used.

        :stability: experimental
        '''
        result = self._values.get("deployment_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deployment_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The timeout for a CodeDeploy deployment.

        :default: - 60 minutes

        :stability: experimental
        '''
        result = self._values.get("deployment_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def deregistration_delay(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The amount of time for ELB to wait before changing the state of a deregistering target from 'draining' to 'unused'.

        :default: - 300 seconds

        :stability: experimental
        '''
        result = self._values.get("deregistration_delay")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def hooks(self) -> typing.Optional[AppSpecHooks]:
        '''(experimental) Optional lifecycle hooks.

        :default: - no lifecycle hooks

        :stability: experimental
        '''
        result = self._values.get("hooks")
        return typing.cast(typing.Optional[AppSpecHooks], result)

    @builtins.property
    def response_time_alarm_threshold(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The threshold for response time alarm.

        :default: - no alarm will be created

        :stability: experimental
        '''
        result = self._values.get("response_time_alarm_threshold")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def target_health_check(
        self,
    ) -> typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck]:
        '''(experimental) The healthcheck to configure on the Application Load Balancer target groups.

        :default: - no health check is configured

        :stability: experimental
        '''
        result = self._values.get("target_health_check")
        return typing.cast(typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck], result)

    @builtins.property
    def termination_wait_time(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The time to wait before terminating the original (blue) task set.

        :default: - 10 minutes

        :stability: experimental
        '''
        result = self._values.get("termination_wait_time")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def test_port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The port to use for test traffic on the listener.

        :default: - listenerPort + 1

        :stability: experimental
        '''
        result = self._values.get("test_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationLoadBalancedCodeDeployedFargateServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-ecs-codedeploy.AwsvpcConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "assign_public_ip": "assignPublicIp",
        "security_groups": "securityGroups",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
    },
)
class AwsvpcConfiguration:
    def __init__(
        self,
        *,
        assign_public_ip: builtins.bool,
        security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        vpc_subnets: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''(experimental) Network configuration for ECS services that have a network type of ``awsvpc``.

        :param assign_public_ip: (experimental) Assign a public IP address to the task.
        :param security_groups: (experimental) The Security Groups to use for the task.
        :param vpc: (experimental) The VPC to use for the task.
        :param vpc_subnets: (experimental) The Subnets to use for the task.

        :stability: experimental
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b51ce7b060a2cbe6ceabb5d4b6d2ebb95a67fd6a0f1ffeb644b04fd89070e6f5)
            check_type(argname="argument assign_public_ip", value=assign_public_ip, expected_type=type_hints["assign_public_ip"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "assign_public_ip": assign_public_ip,
            "security_groups": security_groups,
            "vpc": vpc,
            "vpc_subnets": vpc_subnets,
        }

    @builtins.property
    def assign_public_ip(self) -> builtins.bool:
        '''(experimental) Assign a public IP address to the task.

        :stability: experimental
        '''
        result = self._values.get("assign_public_ip")
        assert result is not None, "Required property 'assign_public_ip' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def security_groups(self) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''(experimental) The Security Groups to use for the task.

        :stability: experimental
        '''
        result = self._values.get("security_groups")
        assert result is not None, "Required property 'security_groups' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC to use for the task.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def vpc_subnets(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''(experimental) The Subnets to use for the task.

        :stability: experimental
        '''
        result = self._values.get("vpc_subnets")
        assert result is not None, "Required property 'vpc_subnets' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsvpcConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EcsAppSpec(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-ecs-codedeploy.EcsAppSpec",
):
    '''(experimental) Represents an AppSpec to be used for ECS services.

    see: https://docs.aws.amazon.com/codedeploy/latest/userguide/reference-appspec-file-structure-resources.html#reference-appspec-file-structure-resources-ecs

    :stability: experimental
    '''

    def __init__(
        self,
        target_service: typing.Union["TargetService", typing.Dict[builtins.str, typing.Any]],
        *,
        after_allow_test_traffic: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
        after_allow_traffic: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
        after_install: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
        before_allow_traffic: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
        before_install: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
    ) -> None:
        '''
        :param target_service: -
        :param after_allow_test_traffic: (experimental) Lambda or ARN of a lambda to run tasks after the test listener serves traffic to the replacement task set.
        :param after_allow_traffic: (experimental) Lambda or ARN of a lambda to run tasks after the second target group serves traffic to the replacement task set.
        :param after_install: (experimental) Lambda or ARN of a lambda to run tasks after the replacement task set is created and one of the target groups is associated with it.
        :param before_allow_traffic: (experimental) Lambda or ARN of a lambda to run tasks after the second target group is associated with the replacement task set, but before traffic is shifted to the replacement task set.
        :param before_install: (experimental) Lambda or ARN of a lambda to run tasks before the replacement task set is created.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7057d61c43e7b1d05c25f97259aa011e7d51296efce331c3d837009b80526708)
            check_type(argname="argument target_service", value=target_service, expected_type=type_hints["target_service"])
        hooks = AppSpecHooks(
            after_allow_test_traffic=after_allow_test_traffic,
            after_allow_traffic=after_allow_traffic,
            after_install=after_install,
            before_allow_traffic=before_allow_traffic,
            before_install=before_install,
        )

        jsii.create(self.__class__, self, [target_service, hooks])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''(experimental) Render JSON string for this AppSpec to be used.

        :return: string representation of this AppSpec

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))


class EcsDeployment(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-ecs-codedeploy.EcsDeployment",
):
    '''(experimental) A CodeDeploy Deployment for a Amazon ECS service DeploymentGroup.

    An EcsDeploymentGroup
    must only have 1 EcsDeployment. This limit is enforced by removing the scope and id
    from the constructor. The scope will always be set to the EcsDeploymentGroup
    and the id will always be set to the string 'Deployment' to force an error if mulitiple
    EcsDeployment constructs are created for a single EcsDeploymentGroup.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        deployment_group: _aws_cdk_aws_codedeploy_ceddda9d.IEcsDeploymentGroup,
        target_service: typing.Union["TargetService", typing.Dict[builtins.str, typing.Any]],
        auto_rollback: typing.Optional[typing.Union[_aws_cdk_aws_codedeploy_ceddda9d.AutoRollbackConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        hooks: typing.Optional[typing.Union[AppSpecHooks, typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param deployment_group: (experimental) The deployment group to target for this deployment.
        :param target_service: (experimental) The ECS service to target for the deployment. see: https://docs.aws.amazon.com/codedeploy/latest/userguide/reference-appspec-file-structure-resources.html#reference-appspec-file-structure-resources-ecs
        :param auto_rollback: (experimental) The configuration for rollback in the event that a deployment fails. Default: : no automatic rollback triggered
        :param description: (experimental) The description for the deployment. Default: no description
        :param hooks: (experimental) Optional lifecycle hooks. Default: - no lifecycle hooks
        :param timeout: (experimental) The timeout for the deployment. If the timeout is reached, it will trigger a rollback of the stack. Default: 30 minutes

        :stability: experimental
        '''
        props = EcsDeploymentProps(
            deployment_group=deployment_group,
            target_service=target_service,
            auto_rollback=auto_rollback,
            description=description,
            hooks=hooks,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property
    @jsii.member(jsii_name="deploymentId")
    def deployment_id(self) -> builtins.str:
        '''(experimental) The id of the deployment that was created.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "deploymentId"))

    @deployment_id.setter
    def deployment_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cc273145c81a5b3feb82f0113f771182606a96ee3a6e364449af965eb95ad92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deploymentId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdklabs/cdk-ecs-codedeploy.EcsDeploymentProps",
    jsii_struct_bases=[],
    name_mapping={
        "deployment_group": "deploymentGroup",
        "target_service": "targetService",
        "auto_rollback": "autoRollback",
        "description": "description",
        "hooks": "hooks",
        "timeout": "timeout",
    },
)
class EcsDeploymentProps:
    def __init__(
        self,
        *,
        deployment_group: _aws_cdk_aws_codedeploy_ceddda9d.IEcsDeploymentGroup,
        target_service: typing.Union["TargetService", typing.Dict[builtins.str, typing.Any]],
        auto_rollback: typing.Optional[typing.Union[_aws_cdk_aws_codedeploy_ceddda9d.AutoRollbackConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        hooks: typing.Optional[typing.Union[AppSpecHooks, typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Construction properties of EcsDeployment.

        :param deployment_group: (experimental) The deployment group to target for this deployment.
        :param target_service: (experimental) The ECS service to target for the deployment. see: https://docs.aws.amazon.com/codedeploy/latest/userguide/reference-appspec-file-structure-resources.html#reference-appspec-file-structure-resources-ecs
        :param auto_rollback: (experimental) The configuration for rollback in the event that a deployment fails. Default: : no automatic rollback triggered
        :param description: (experimental) The description for the deployment. Default: no description
        :param hooks: (experimental) Optional lifecycle hooks. Default: - no lifecycle hooks
        :param timeout: (experimental) The timeout for the deployment. If the timeout is reached, it will trigger a rollback of the stack. Default: 30 minutes

        :stability: experimental
        '''
        if isinstance(target_service, dict):
            target_service = TargetService(**target_service)
        if isinstance(auto_rollback, dict):
            auto_rollback = _aws_cdk_aws_codedeploy_ceddda9d.AutoRollbackConfig(**auto_rollback)
        if isinstance(hooks, dict):
            hooks = AppSpecHooks(**hooks)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__baf38974d86829a66d2716f1cb94150364c1bbca49159ddfb7ca3933cbcc14cb)
            check_type(argname="argument deployment_group", value=deployment_group, expected_type=type_hints["deployment_group"])
            check_type(argname="argument target_service", value=target_service, expected_type=type_hints["target_service"])
            check_type(argname="argument auto_rollback", value=auto_rollback, expected_type=type_hints["auto_rollback"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument hooks", value=hooks, expected_type=type_hints["hooks"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "deployment_group": deployment_group,
            "target_service": target_service,
        }
        if auto_rollback is not None:
            self._values["auto_rollback"] = auto_rollback
        if description is not None:
            self._values["description"] = description
        if hooks is not None:
            self._values["hooks"] = hooks
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def deployment_group(self) -> _aws_cdk_aws_codedeploy_ceddda9d.IEcsDeploymentGroup:
        '''(experimental) The deployment group to target for this deployment.

        :stability: experimental
        '''
        result = self._values.get("deployment_group")
        assert result is not None, "Required property 'deployment_group' is missing"
        return typing.cast(_aws_cdk_aws_codedeploy_ceddda9d.IEcsDeploymentGroup, result)

    @builtins.property
    def target_service(self) -> "TargetService":
        '''(experimental) The ECS service to target for the deployment.

        see: https://docs.aws.amazon.com/codedeploy/latest/userguide/reference-appspec-file-structure-resources.html#reference-appspec-file-structure-resources-ecs

        :stability: experimental
        '''
        result = self._values.get("target_service")
        assert result is not None, "Required property 'target_service' is missing"
        return typing.cast("TargetService", result)

    @builtins.property
    def auto_rollback(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.AutoRollbackConfig]:
        '''(experimental) The configuration for rollback in the event that a deployment fails.

        :default: : no automatic rollback triggered

        :stability: experimental
        '''
        result = self._values.get("auto_rollback")
        return typing.cast(typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.AutoRollbackConfig], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description for the deployment.

        :default: no description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hooks(self) -> typing.Optional[AppSpecHooks]:
        '''(experimental) Optional lifecycle hooks.

        :default: - no lifecycle hooks

        :stability: experimental
        '''
        result = self._values.get("hooks")
        return typing.cast(typing.Optional[AppSpecHooks], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The timeout for the deployment.

        If the timeout is reached, it will trigger a rollback of the stack.

        :default: 30 minutes

        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EcsDeploymentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-ecs-codedeploy.TargetService",
    jsii_struct_bases=[],
    name_mapping={
        "container_name": "containerName",
        "container_port": "containerPort",
        "task_definition": "taskDefinition",
        "awsvpc_configuration": "awsvpcConfiguration",
        "capacity_provider_strategy": "capacityProviderStrategy",
        "platform_version": "platformVersion",
    },
)
class TargetService:
    def __init__(
        self,
        *,
        container_name: builtins.str,
        container_port: jsii.Number,
        task_definition: _aws_cdk_aws_ecs_ceddda9d.ITaskDefinition,
        awsvpc_configuration: typing.Optional[typing.Union[AwsvpcConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        capacity_provider_strategy: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
        platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
    ) -> None:
        '''(experimental) Describe the target for CodeDeploy to use when creating a deployment for an ecs.EcsDeploymentGroup.

        :param container_name: (experimental) The name of the Amazon ECS container that contains your Amazon ECS application. It must be a container specified in your Amazon ECS task definition.
        :param container_port: (experimental) The port on the container where traffic will be routed to.
        :param task_definition: (experimental) The TaskDefintion to deploy to the target services.
        :param awsvpc_configuration: (experimental) Network configuration for ECS services that have a network type of ``awsvpc``. Default: reuse current network settings for ECS service.
        :param capacity_provider_strategy: (experimental) A list of Amazon ECS capacity providers to use for the deployment. Default: reuse current capcity provider strategy for ECS service.
        :param platform_version: (experimental) The platform version of the Fargate tasks in the deployed Amazon ECS service. see: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html Default: LATEST

        :stability: experimental
        '''
        if isinstance(awsvpc_configuration, dict):
            awsvpc_configuration = AwsvpcConfiguration(**awsvpc_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db7eb4e0817d1687cd8f3473d1eb1b9ce0f34b1150ba396c6c7b62edcdef0342)
            check_type(argname="argument container_name", value=container_name, expected_type=type_hints["container_name"])
            check_type(argname="argument container_port", value=container_port, expected_type=type_hints["container_port"])
            check_type(argname="argument task_definition", value=task_definition, expected_type=type_hints["task_definition"])
            check_type(argname="argument awsvpc_configuration", value=awsvpc_configuration, expected_type=type_hints["awsvpc_configuration"])
            check_type(argname="argument capacity_provider_strategy", value=capacity_provider_strategy, expected_type=type_hints["capacity_provider_strategy"])
            check_type(argname="argument platform_version", value=platform_version, expected_type=type_hints["platform_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "container_name": container_name,
            "container_port": container_port,
            "task_definition": task_definition,
        }
        if awsvpc_configuration is not None:
            self._values["awsvpc_configuration"] = awsvpc_configuration
        if capacity_provider_strategy is not None:
            self._values["capacity_provider_strategy"] = capacity_provider_strategy
        if platform_version is not None:
            self._values["platform_version"] = platform_version

    @builtins.property
    def container_name(self) -> builtins.str:
        '''(experimental) The name of the Amazon ECS container that contains your Amazon ECS application.

        It must be a container specified in your Amazon ECS task definition.

        :stability: experimental
        '''
        result = self._values.get("container_name")
        assert result is not None, "Required property 'container_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def container_port(self) -> jsii.Number:
        '''(experimental) The port on the container where traffic will be routed to.

        :stability: experimental
        '''
        result = self._values.get("container_port")
        assert result is not None, "Required property 'container_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def task_definition(self) -> _aws_cdk_aws_ecs_ceddda9d.ITaskDefinition:
        '''(experimental) The TaskDefintion to deploy to the target services.

        :stability: experimental
        '''
        result = self._values.get("task_definition")
        assert result is not None, "Required property 'task_definition' is missing"
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.ITaskDefinition, result)

    @builtins.property
    def awsvpc_configuration(self) -> typing.Optional[AwsvpcConfiguration]:
        '''(experimental) Network configuration for ECS services that have a network type of ``awsvpc``.

        :default: reuse current network settings for ECS service.

        :stability: experimental
        '''
        result = self._values.get("awsvpc_configuration")
        return typing.cast(typing.Optional[AwsvpcConfiguration], result)

    @builtins.property
    def capacity_provider_strategy(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy]]:
        '''(experimental) A list of Amazon ECS capacity providers to use for the deployment.

        :default: reuse current capcity provider strategy for ECS service.

        :stability: experimental
        '''
        result = self._values.get("capacity_provider_strategy")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy]], result)

    @builtins.property
    def platform_version(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion]:
        '''(experimental) The platform version of the Fargate tasks in the deployed Amazon ECS service.

        see: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html

        :default: LATEST

        :stability: experimental
        '''
        result = self._values.get("platform_version")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TargetService(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApiCanary",
    "ApiCanaryProps",
    "ApiTestStep",
    "AppSpecHooks",
    "ApplicationLoadBalancedCodeDeployedFargateService",
    "ApplicationLoadBalancedCodeDeployedFargateServiceProps",
    "AwsvpcConfiguration",
    "EcsAppSpec",
    "EcsDeployment",
    "EcsDeploymentProps",
    "TargetService",
]

publication.publish()

def _typecheckingstub__191f9116e56adec234abc14306f9567b253f56a52ebb603f3f2db855fff52cbc(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    base_url: builtins.str,
    artifacts_bucket_location: typing.Optional[typing.Union[_aws_cdk_aws_synthetics_ceddda9d.ArtifactsBucketLocation, typing.Dict[builtins.str, typing.Any]]] = None,
    canary_name: typing.Optional[builtins.str] = None,
    duration_alarm_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    failure_retention_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    schedule: typing.Optional[_aws_cdk_aws_synthetics_ceddda9d.Schedule] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    start_after_creation: typing.Optional[builtins.bool] = None,
    steps: typing.Optional[typing.Sequence[typing.Union[ApiTestStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    success_retention_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    thread_count: typing.Optional[jsii.Number] = None,
    time_to_live: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8421acef4559e3bdccb095c272a6b29bf9e4dd210557d600e8932b033d21e07(
    value: _aws_cdk_aws_cloudwatch_ceddda9d.Alarm,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44a7b96ff37721539a356fa80f06c31f2594735a95565d63e168dc4160b4caf5(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Alarm],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88653fc398cb7758d2ca950230ea75e3ed2418d64533c67731fcb689cc5e7fc9(
    *,
    base_url: builtins.str,
    artifacts_bucket_location: typing.Optional[typing.Union[_aws_cdk_aws_synthetics_ceddda9d.ArtifactsBucketLocation, typing.Dict[builtins.str, typing.Any]]] = None,
    canary_name: typing.Optional[builtins.str] = None,
    duration_alarm_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    failure_retention_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    schedule: typing.Optional[_aws_cdk_aws_synthetics_ceddda9d.Schedule] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    start_after_creation: typing.Optional[builtins.bool] = None,
    steps: typing.Optional[typing.Sequence[typing.Union[ApiTestStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    success_retention_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    thread_count: typing.Optional[jsii.Number] = None,
    time_to_live: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d90c3a4104ecc8b3454055531f4b23054219c9454abf72a0f58b4992241a296(
    *,
    name: builtins.str,
    path: builtins.str,
    body: typing.Optional[builtins.str] = None,
    expected_value: typing.Any = None,
    headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    jmes_path: typing.Optional[builtins.str] = None,
    method: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87d5882f317f0c77b4b3020db23e892ee7831c1c15bdc09ffc0cd0be4c287bba(
    *,
    after_allow_test_traffic: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
    after_allow_traffic: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
    after_install: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
    before_allow_traffic: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
    before_install: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6736d1d0b574dec7792a72d160022fb3d36b354822af032896dd4f37f5ca9b8f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    access_log_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    access_log_prefix: typing.Optional[builtins.str] = None,
    api_canary_schedule: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    api_canary_thread_count: typing.Optional[jsii.Number] = None,
    api_canary_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    api_test_steps: typing.Optional[typing.Sequence[typing.Union[ApiTestStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    application_name: typing.Optional[builtins.str] = None,
    deployment_config: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IEcsDeploymentConfig] = None,
    deployment_group_name: typing.Optional[builtins.str] = None,
    deployment_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    deregistration_delay: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    hooks: typing.Optional[typing.Union[AppSpecHooks, typing.Dict[builtins.str, typing.Any]]] = None,
    response_time_alarm_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    target_health_check: typing.Optional[typing.Union[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    termination_wait_time: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    test_port: typing.Optional[jsii.Number] = None,
    assign_public_ip: typing.Optional[builtins.bool] = None,
    health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    task_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
    certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
    cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
    deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
    desired_count: typing.Optional[jsii.Number] = None,
    domain_name: typing.Optional[builtins.str] = None,
    domain_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
    enable_execute_command: typing.Optional[builtins.bool] = None,
    health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    listener_port: typing.Optional[jsii.Number] = None,
    load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer] = None,
    load_balancer_name: typing.Optional[builtins.str] = None,
    max_healthy_percent: typing.Optional[jsii.Number] = None,
    min_healthy_percent: typing.Optional[jsii.Number] = None,
    open_listener: typing.Optional[builtins.bool] = None,
    propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
    protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
    public_load_balancer: typing.Optional[builtins.bool] = None,
    record_type: typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType] = None,
    redirect_http: typing.Optional[builtins.bool] = None,
    service_name: typing.Optional[builtins.str] = None,
    ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
    target_protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    task_image_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    cpu: typing.Optional[jsii.Number] = None,
    ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
    memory_limit_mib: typing.Optional[jsii.Number] = None,
    platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
    runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
    task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c9be01440d9f934df9cd543843f7c6cedddf85074119c83a9dc135e7f624ad6(
    service: _aws_cdk_aws_ecs_ceddda9d.BaseService,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7447c7e10dcde2ca43c49add170830026b87ed7d494c7d26cfab83f894422f58(
    value: _aws_cdk_aws_s3_ceddda9d.IBucket,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19f6fc9043e008683908ea78ba0046c1ab7547e85d051ddfc1c2fda80aaaa948(
    value: _aws_cdk_aws_codedeploy_ceddda9d.EcsApplication,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__311404106c32389cecdf74bfa60f61a4655e983615508a7acd9f4bd9b24ce958(
    value: EcsDeployment,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ea1e4a8c09ecded833b997f80fb0e9df7eac4e09fd6bdfb81c0c3be8f653aad(
    value: _aws_cdk_aws_codedeploy_ceddda9d.EcsDeploymentGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f4dbd3c75011f6cdb6230ceac17e417f8695b3dbbb5308e679013801a287934(
    value: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationTargetGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__588edfc0c2963040dfc1d1d6d3818d3d4db18e61f20734f62776940b00eb5b88(
    value: _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListener,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ccaa296e9a9496ff6b2bdf82b089f13e1d085ab5e7ae45642938930901923e3(
    value: typing.Optional[ApiCanary],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d150c4633641ccb074c83db146501c42346deda1c4eec3ca8929f59d0523898(
    value: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27c0c490ffab55452beb7a0943b27b71229ff007f255832d362d9af91fbe01b9(
    *,
    capacity_provider_strategies: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
    certificate: typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate] = None,
    circuit_breaker: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentCircuitBreaker, typing.Dict[builtins.str, typing.Any]]] = None,
    cloud_map_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CloudMapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.ICluster] = None,
    deployment_controller: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.DeploymentController, typing.Dict[builtins.str, typing.Any]]] = None,
    desired_count: typing.Optional[jsii.Number] = None,
    domain_name: typing.Optional[builtins.str] = None,
    domain_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    enable_ecs_managed_tags: typing.Optional[builtins.bool] = None,
    enable_execute_command: typing.Optional[builtins.bool] = None,
    health_check_grace_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    idle_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    listener_port: typing.Optional[jsii.Number] = None,
    load_balancer: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.IApplicationLoadBalancer] = None,
    load_balancer_name: typing.Optional[builtins.str] = None,
    max_healthy_percent: typing.Optional[jsii.Number] = None,
    min_healthy_percent: typing.Optional[jsii.Number] = None,
    open_listener: typing.Optional[builtins.bool] = None,
    propagate_tags: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.PropagatedTagSource] = None,
    protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    protocol_version: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocolVersion] = None,
    public_load_balancer: typing.Optional[builtins.bool] = None,
    record_type: typing.Optional[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedServiceRecordType] = None,
    redirect_http: typing.Optional[builtins.bool] = None,
    service_name: typing.Optional[builtins.str] = None,
    ssl_policy: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.SslPolicy] = None,
    target_protocol: typing.Optional[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationProtocol] = None,
    task_image_options: typing.Optional[typing.Union[_aws_cdk_aws_ecs_patterns_ceddda9d.ApplicationLoadBalancedTaskImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    cpu: typing.Optional[jsii.Number] = None,
    ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
    memory_limit_mib: typing.Optional[jsii.Number] = None,
    platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
    runtime_platform: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.RuntimePlatform, typing.Dict[builtins.str, typing.Any]]] = None,
    task_definition: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition] = None,
    assign_public_ip: typing.Optional[builtins.bool] = None,
    health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    task_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    access_log_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    access_log_prefix: typing.Optional[builtins.str] = None,
    api_canary_schedule: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    api_canary_thread_count: typing.Optional[jsii.Number] = None,
    api_canary_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    api_test_steps: typing.Optional[typing.Sequence[typing.Union[ApiTestStep, typing.Dict[builtins.str, typing.Any]]]] = None,
    application_name: typing.Optional[builtins.str] = None,
    deployment_config: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IEcsDeploymentConfig] = None,
    deployment_group_name: typing.Optional[builtins.str] = None,
    deployment_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    deregistration_delay: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    hooks: typing.Optional[typing.Union[AppSpecHooks, typing.Dict[builtins.str, typing.Any]]] = None,
    response_time_alarm_threshold: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    target_health_check: typing.Optional[typing.Union[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    termination_wait_time: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    test_port: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b51ce7b060a2cbe6ceabb5d4b6d2ebb95a67fd6a0f1ffeb644b04fd89070e6f5(
    *,
    assign_public_ip: builtins.bool,
    security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    vpc_subnets: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7057d61c43e7b1d05c25f97259aa011e7d51296efce331c3d837009b80526708(
    target_service: typing.Union[TargetService, typing.Dict[builtins.str, typing.Any]],
    *,
    after_allow_test_traffic: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
    after_allow_traffic: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
    after_install: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
    before_allow_traffic: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
    before_install: typing.Optional[typing.Union[builtins.str, _aws_cdk_aws_lambda_ceddda9d.IFunction]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cc273145c81a5b3feb82f0113f771182606a96ee3a6e364449af965eb95ad92(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__baf38974d86829a66d2716f1cb94150364c1bbca49159ddfb7ca3933cbcc14cb(
    *,
    deployment_group: _aws_cdk_aws_codedeploy_ceddda9d.IEcsDeploymentGroup,
    target_service: typing.Union[TargetService, typing.Dict[builtins.str, typing.Any]],
    auto_rollback: typing.Optional[typing.Union[_aws_cdk_aws_codedeploy_ceddda9d.AutoRollbackConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    hooks: typing.Optional[typing.Union[AppSpecHooks, typing.Dict[builtins.str, typing.Any]]] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db7eb4e0817d1687cd8f3473d1eb1b9ce0f34b1150ba396c6c7b62edcdef0342(
    *,
    container_name: builtins.str,
    container_port: jsii.Number,
    task_definition: _aws_cdk_aws_ecs_ceddda9d.ITaskDefinition,
    awsvpc_configuration: typing.Optional[typing.Union[AwsvpcConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    capacity_provider_strategy: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CapacityProviderStrategy, typing.Dict[builtins.str, typing.Any]]]] = None,
    platform_version: typing.Optional[_aws_cdk_aws_ecs_ceddda9d.FargatePlatformVersion] = None,
) -> None:
    """Type checking stubs"""
    pass
