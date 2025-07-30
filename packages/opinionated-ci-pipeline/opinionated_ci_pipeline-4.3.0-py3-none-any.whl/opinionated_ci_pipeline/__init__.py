r'''
# Opinionated CDK CI Pipeline

[![NPM](https://img.shields.io/npm/v/opinionated-ci-pipeline?color=blue)](https://www.npmjs.com/package/opinionated-ci-pipeline)
[![PyPI](https://img.shields.io/pypi/v/opinionated-ci-pipeline?color=blue)](https://pypi.org/project/opinionated-ci-pipeline/)

CI/CD utilizing [CDK Pipelines](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.pipelines-readme.html).

Features:

* pipeline deploying application from the default branch
  to multiple environments on multiple accounts,
* feature branch deployments to ephemeral environments,
* development environments deployments from the local CLI,
* build status notifications to repository commits,
* build failures notifications to SNS,
* supports commit message tags to skip deployments (`[skip ci]` or `[no ci]`).

Currently supported source repositories are GitHub and Bitbucket.

Pipeline architecture:

![Pipeline architecture](.github/architecture.png)

See the [announcement blog post](https://articles.merapar.com/finally-the-cdk-ci-pipeline-that-serverless-deserves) for more details and examples.

## Table of contents

* [Table of contents](#table-of-contents)
* [Usage](#usage)

  * [1. Install](#1-install)
  * [2. Set context parameters](#2-set-context-parameters)
  * [3. Create `CDKApplication`](#3-create-cdkapplication)
  * [4. Create repository access token](#4-create-repository-access-token)

    * [GitHub](#github)
    * [Bitbucket](#bitbucket)
  * [5. Bootstrap the CDK](#5-bootstrap-the-cdk)
  * [6. Deploy the CI Stack](#6-deploy-the-ci-stack)
  * [Deploy development environment](#deploy-development-environment)
* [Parameters](#parameters)
* [Notifications and alarms](#notifications-and-alarms)
* [How to](#how-to)

  * [Run unit tests during build](#run-unit-tests-during-build)
  * [Enable Docker](#enable-docker)
* [Library development](#library-development)

## Usage

To set up, you need to complete the following steps:

1. Install the library in your project.
2. Specify context parameters.
3. Create `CDKApplication` with build process configuration.
4. Create repository access token.
5. Bootstrap the CDK on the AWS account(s).
6. Deploy the CI.

At the end, you will have CI pipeline in place,
and be able to deploy your own custom environment from the CLI as well.

### 1. Install

For Node.js:

```bash
npm install -D opinionated-ci-pipeline
```

For Python:

```bash
pip install opinionated-ci-pipeline
```

### 2. Set context parameters

Add project name and environments config in the `cdk.json` as `context` parameters.
Each environment must have `account` and `region` provided.

```json
{
  "app": "...",
  "context": {
    "projectName": "myproject",
    "environments": {
      "default": {
        "account": "111111111111",
        "region": "us-east-1"
      },
      "prod": {
        "account": "222222222222",
        "region": "us-east-1"
      }
    }
  }
}
```

The project name will be used as a prefix for the deployed CI Stack name.

Environment names should match environments provided later
in the `CDKApplication` configuration.

The optional `default` environment configuration is used as a fallback.

The CI pipeline itself is deployed to the `ci` environment,
with a fallback to the `default` environment as well.

### 3. Create `CDKApplication`

In the CDK entrypoint script referenced by the `cdk.json` `app` field,
replace the content with an instance of `CDKApplication`:

```python
#!/usr/bin/env node
import 'source-map-support/register';
import {ExampleStack} from '../lib/exampleStack';
import {CDKApplication} from 'opinionated-ci-pipeline';

new CDKApplication({
    stacks: {
        create: (scope, projectName, envName) => {
            new ExampleStack(scope, 'ExampleStack', {stackName: `${projectName}-${envName}-ExampleStack`});
        },
    },
    repository: {
        host: 'github',
        name: 'organization/repository',
    },
    packageManager: 'npm',
    pipeline: [
        {
            environment: 'test',
            post: [
                'echo "do integration tests here"',
            ],
        },
        {
            environment: 'prod',
        },
    ],
});
```

This configures the application with one Stack
and a pipeline deploying to an environment `test`,
running integration tests, and deploying to environment `prod`.

The `test` and `prod` environments will be deployed
from the branch `main` (by default).
All other branches will be deployed to separate environments.
Those feature-branch environments will be destroyed after the branch is removed.

To allow deployment of multiple environments,
the Stack(s) name must include the environment name.

### 4. Create repository access token

An access to the source repository is required
to fetch code and send build status notifications.

Once access token is created, save it in SSM Parameter Store
as a `SecureString` under the path `/{projectName}/ci/repositoryAccessToken`.

See instructions below on how to create the token
for each supported repository host.

#### GitHub

Create [a fine-grained personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token#creating-a-fine-grained-personal-access-token)
with read-only access for `Contents`
read and write access for `Commit statuses` and `Webhooks`.

#### Bitbucket

In Bitbucket, go to your repository.
Open Settings → Access tokens.
There, create a new Repository Access Token
with `repository:write` and `webhook` scopes.

### 5. Bootstrap the CDK

[Bootstrap the CDK](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html)
on the account holding the CI pipeline
and all other accounts the pipeline will be deploying to.

When bootstrapping other accounts, add the `--trust` parameter
with the account ID of the account holding the pipeline.

### 6. Deploy the CI Stack

Run:

```bash
cdk deploy -c ci=true
```

### Deploy development environment

Run:

```bash
cdk deploy -c env=MYENV --all
```

to deploy arbitrary environments.

## Parameters

<table>
    <tr>
        <th>Name</th>
        <th>Type</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>stacks</td>
        <td>object</td>
        <td>
An object with a create() method to create Stacks for the application.
<br/>
The same Stacks will be deployed with main pipeline, feature-branch builds, and local deployments.
        </td>
    </tr>
    <tr>
        <td>packageManager</td>
        <td>npm | pnpm</td>
        <td>
Package manager used in the repository.
<br/>

If provided, the `install` command will be set to install dependencies using given package manager.

</td>
    </tr>
    <tr>
        <td>commands</td>
        <td>object</td>
        <td>

Commands executed to build and deploy the application.
<br/>
The following commands are set by default:

* `install`
* `synthPipeline`
* `deployEnvironment`
* `destroyEnvironment`

If you override the `install` command,
either install the `aws-cdk@2` globally
or modify the other 3 commands to use the local `cdk` binary.
<br/>
Commands executed on particular builds:

* main pipeline:

  * `preInstall`
  * `install`
  * `buildAndTest`
  * `synthPipeline`
* feature branch environment deployment:

  * `preInstall`
  * `install`
  * `buildAndTest`
  * `preDeployEnvironment`
  * `deployEnvironment`
  * `postDeployEnvironment`
* feature branch environment destruction:

  * `preInstall`
  * `install`
  * `preDestroyEnvironment`
  * `destroyEnvironment`
  * `postDestroyEnvironment`

    </td>
    </tr>
    <tr>
        <td>cdkOutputDirectory</td>
        <td>string</td>
        <td>

The location where CDK outputs synthetized files.
Corresponds to the CDK Pipelines `ShellStepProps#primaryOutputDirectory`.

</td>
      </tr>
      <tr>
          <td>pipeline</td>
          <td>object[]</td>
          <td>
CodePipeline deployment pipeline for the main repository branch.
<br/>
Can contain environments to deploy
and waves that deploy multiple environments in parallel.
<br/>
Each environment and wave can have pre and post commands
that will be executed before and after the environment or wave deployment.
            </td>
      </tr>
      <tr>
          <td>codeBuild</td>
          <td>object</td>
          <td>
Override CodeBuild properties, used for the main pipeline
as well as feature branch ephemeral environments deploys and destroys.
</td>
      </tr>
      <tr>
          <td>codePipeline</td>
          <td>object</td>
          <td>Override CodePipeline properties.</td>
      </tr>
      <tr>
          <td>slackNotifications</td>
          <td>object</td>
          <td>
Configuration for Slack notifications.
Requires configuring AWS Chatbot client manually first.
</td>
      </tr>
      <tr>
          <td>fixPathsMetadata</td>
          <td>boolean</td>
          <td>

Whether to remove the CI resources
from the beginning of the `aws:cdk:path` metadata
when deploying from the main pipeline.

</td>
      </tr>
</table>

## Notifications and alarms

Stack creates SNS Topics with notifications for
main pipeline failures and feature branch build failures.
Their ARNs are saved in SSM Parameters and outputed by the stack:

* main pipeline failures:

  * SSM: `/{projectName}/ci/pipelineFailuresTopicArn`
  * Stack exported output: `{projectName}-ci-pipelineFailuresTopicArn`
* feature branch build failures:

  * SSM: `/{projectName}/ci/featureBranchBuildFailuresTopicArn`
  * Stack exported output: `{projectName}-ci-featureBranchBuildFailuresTopicArn`

If you setup Slack notifications,
you can configure those failure notifications to be sent to Slack.

Moreover, if you setup Slack notifications,
an additional SNS Topic will be created
to which you can send CloudWatch Alarms.
It's ARN is provided:

* SSM: `/{projectName}/ci/slackAlarmsTopicArn`
* Stack exported output: `{projectName}-ci-slackAlarmsTopicArn`

## How to

### Run unit tests during build

Set commands in the `commands.buildAndTest`:

```python
{
    commands: {
        buildAndTest: [
            'npm run lint',
            'npm run test',
        ]
    }
}
```

### Enable Docker

Set `codeBuild.buildEnvironment.privileged` to `true`:

```python
{
    codeBuild: {
        buildEnvironment: {
            privileged: true
        }
    }
}
```

## Library development

Project uses [jsii](https://aws.github.io/jsii/)
to generate packages for different languages.

Install dependencies:

```bash
npm install
```

Build:

```bash
npm run build
```

Change `example/bin/cdk.ts` `repository` to point to your repository.

Then, install and deploy the CI for the example application:

```bash
cd example
pnpm install
pnpm cdk deploy -c ci=true
```

One-line command to re-deploy after changes (run from the `example` directory):

```bash
(cd .. && npm run build && cd example && cdk deploy -m direct -c ci=true)
```
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
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.pipelines as _aws_cdk_pipelines_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="opinionated-ci-pipeline.ApplicationProps",
    jsii_struct_bases=[],
    name_mapping={
        "pipeline": "pipeline",
        "repository": "repository",
        "stacks": "stacks",
        "cdk_output_directory": "cdkOutputDirectory",
        "code_build": "codeBuild",
        "code_pipeline": "codePipeline",
        "commands": "commands",
        "fix_paths_metadata": "fixPathsMetadata",
        "package_manager": "packageManager",
        "prefix_stack_id_with_project_name": "prefixStackIdWithProjectName",
        "slack_notifications": "slackNotifications",
    },
)
class ApplicationProps:
    def __init__(
        self,
        *,
        pipeline: typing.Sequence[typing.Union[typing.Union["WaveDeployment", typing.Dict[builtins.str, typing.Any]], typing.Union["EnvironmentDeployment", typing.Dict[builtins.str, typing.Any]]]],
        repository: typing.Union["RepositoryProps", typing.Dict[builtins.str, typing.Any]],
        stacks: "IStacksCreation",
        cdk_output_directory: typing.Optional[builtins.str] = None,
        code_build: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        code_pipeline: typing.Optional[typing.Union["CodePipelineOverrides", typing.Dict[builtins.str, typing.Any]]] = None,
        commands: typing.Optional[typing.Union["BuildCommands", typing.Dict[builtins.str, typing.Any]]] = None,
        fix_paths_metadata: typing.Optional[builtins.bool] = None,
        package_manager: typing.Optional[builtins.str] = None,
        prefix_stack_id_with_project_name: typing.Optional[builtins.bool] = None,
        slack_notifications: typing.Optional[typing.Union["SlackNotifications", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param pipeline: CodePipeline deployment pipeline for the main repository branch. Can contain environments to deploy and waves that deploy multiple environments in parallel. Each environment and wave can have pre and post commands that will be executed before and after the environment or wave deployment.
        :param repository: 
        :param stacks: An object with a create() method to create Stacks for the application. The same Stacks will be deployed with main pipeline, feature-branch builds, and local deployments.
        :param cdk_output_directory: The location where CDK outputs synthetized files. Corresponds to the CDK Pipelines ShellStepProps#primaryOutputDirectory. Default: cdk.out
        :param code_build: Override CodeBuild properties, used for the main pipeline Build step as well as feature branch ephemeral environments deploys and destroys. Default: 1 hour timeout, compute type MEDIUM with Linux build image Standard 7.0
        :param code_pipeline: Override CodePipeline properties. Default: Don't use change sets
        :param commands: Commands executed to build and deploy the application.
        :param fix_paths_metadata: Whether to remove the CI resources from the beginning of the aws:cdk:path metadata. Enabling it results in the same tree view in the CloudFormation Console as with manual deployment though the CLI. Without it, the tree view for the stacks deployed through the CI starts with the 3 extra levels. This also prevents updating all resources just to change their metadata when deploying the stack alternately from the CI and CLI. This DOES NOT change the paths themselves, only the metadata. The resources that use the full path in their logical IDs (like the ``EventSourceMapping`` created with ``lambda.addEventSource()``) will still change. Default: false
        :param package_manager: Package manager used in the repository. If provided, the install commands will be set to install dependencies using given package manager.
        :param prefix_stack_id_with_project_name: Whether to prefix the CI Stack Construct ID with the project name. Prefixing assures the ID is unique, required in projects deploying multiple CI Pipelines. No-prefixing is for backwards compatibility with existing projects, where changing the Construct ID of the CI Stack would change the Logical IDs of some constructs (like Lambda EventSourceMapping, API Gateway ApiMapping) causing CloudFormation to try re-creating them and fail. Default: true
        :param slack_notifications: Configuration for Slack notifications. Requires configuring AWS Chatbot client manually first.
        '''
        if isinstance(repository, dict):
            repository = RepositoryProps(**repository)
        if isinstance(code_build, dict):
            code_build = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(**code_build)
        if isinstance(code_pipeline, dict):
            code_pipeline = CodePipelineOverrides(**code_pipeline)
        if isinstance(commands, dict):
            commands = BuildCommands(**commands)
        if isinstance(slack_notifications, dict):
            slack_notifications = SlackNotifications(**slack_notifications)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d22629910ce624c4144f7d3a67b45ba1c7b1018575c9f66d6177bc139efb6eb9)
            check_type(argname="argument pipeline", value=pipeline, expected_type=type_hints["pipeline"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument stacks", value=stacks, expected_type=type_hints["stacks"])
            check_type(argname="argument cdk_output_directory", value=cdk_output_directory, expected_type=type_hints["cdk_output_directory"])
            check_type(argname="argument code_build", value=code_build, expected_type=type_hints["code_build"])
            check_type(argname="argument code_pipeline", value=code_pipeline, expected_type=type_hints["code_pipeline"])
            check_type(argname="argument commands", value=commands, expected_type=type_hints["commands"])
            check_type(argname="argument fix_paths_metadata", value=fix_paths_metadata, expected_type=type_hints["fix_paths_metadata"])
            check_type(argname="argument package_manager", value=package_manager, expected_type=type_hints["package_manager"])
            check_type(argname="argument prefix_stack_id_with_project_name", value=prefix_stack_id_with_project_name, expected_type=type_hints["prefix_stack_id_with_project_name"])
            check_type(argname="argument slack_notifications", value=slack_notifications, expected_type=type_hints["slack_notifications"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "pipeline": pipeline,
            "repository": repository,
            "stacks": stacks,
        }
        if cdk_output_directory is not None:
            self._values["cdk_output_directory"] = cdk_output_directory
        if code_build is not None:
            self._values["code_build"] = code_build
        if code_pipeline is not None:
            self._values["code_pipeline"] = code_pipeline
        if commands is not None:
            self._values["commands"] = commands
        if fix_paths_metadata is not None:
            self._values["fix_paths_metadata"] = fix_paths_metadata
        if package_manager is not None:
            self._values["package_manager"] = package_manager
        if prefix_stack_id_with_project_name is not None:
            self._values["prefix_stack_id_with_project_name"] = prefix_stack_id_with_project_name
        if slack_notifications is not None:
            self._values["slack_notifications"] = slack_notifications

    @builtins.property
    def pipeline(
        self,
    ) -> typing.List[typing.Union["WaveDeployment", "EnvironmentDeployment"]]:
        '''CodePipeline deployment pipeline for the main repository branch.

        Can contain environments to deploy
        and waves that deploy multiple environments in parallel.

        Each environment and wave can have pre and post commands
        that will be executed before and after the environment or wave deployment.
        '''
        result = self._values.get("pipeline")
        assert result is not None, "Required property 'pipeline' is missing"
        return typing.cast(typing.List[typing.Union["WaveDeployment", "EnvironmentDeployment"]], result)

    @builtins.property
    def repository(self) -> "RepositoryProps":
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast("RepositoryProps", result)

    @builtins.property
    def stacks(self) -> "IStacksCreation":
        '''An object with a create() method to create Stacks for the application.

        The same Stacks will be deployed with main pipeline, feature-branch builds, and local deployments.
        '''
        result = self._values.get("stacks")
        assert result is not None, "Required property 'stacks' is missing"
        return typing.cast("IStacksCreation", result)

    @builtins.property
    def cdk_output_directory(self) -> typing.Optional[builtins.str]:
        '''The location where CDK outputs synthetized files.

        Corresponds to the CDK Pipelines ShellStepProps#primaryOutputDirectory.

        :default: cdk.out
        '''
        result = self._values.get("cdk_output_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def code_build(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions]:
        '''Override CodeBuild properties, used for the main pipeline Build step as well as feature branch ephemeral environments deploys and destroys.

        :default: 1 hour timeout, compute type MEDIUM with Linux build image Standard 7.0
        '''
        result = self._values.get("code_build")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions], result)

    @builtins.property
    def code_pipeline(self) -> typing.Optional["CodePipelineOverrides"]:
        '''Override CodePipeline properties.

        :default: Don't use change sets
        '''
        result = self._values.get("code_pipeline")
        return typing.cast(typing.Optional["CodePipelineOverrides"], result)

    @builtins.property
    def commands(self) -> typing.Optional["BuildCommands"]:
        '''Commands executed to build and deploy the application.'''
        result = self._values.get("commands")
        return typing.cast(typing.Optional["BuildCommands"], result)

    @builtins.property
    def fix_paths_metadata(self) -> typing.Optional[builtins.bool]:
        '''Whether to remove the CI resources from the beginning of the aws:cdk:path metadata.

        Enabling it results in the same tree view in the CloudFormation Console as with manual deployment though the CLI.
        Without it, the tree view for the stacks deployed through the CI starts with the 3 extra levels.

        This also prevents updating all resources just to change their metadata
        when deploying the stack alternately from the CI and CLI.

        This DOES NOT change the paths themselves, only the metadata.
        The resources that use the full path in their logical IDs
        (like the ``EventSourceMapping`` created with ``lambda.addEventSource()``) will still change.

        :default: false
        '''
        result = self._values.get("fix_paths_metadata")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def package_manager(self) -> typing.Optional[builtins.str]:
        '''Package manager used in the repository.

        If provided, the install commands will be set to install dependencies using given package manager.
        '''
        result = self._values.get("package_manager")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix_stack_id_with_project_name(self) -> typing.Optional[builtins.bool]:
        '''Whether to prefix the CI Stack Construct ID with the project name.

        Prefixing assures the ID is unique, required in projects deploying multiple CI Pipelines.

        No-prefixing is for backwards compatibility with existing projects,
        where changing the Construct ID of the CI Stack would change the Logical IDs of some constructs
        (like Lambda EventSourceMapping, API Gateway ApiMapping)
        causing CloudFormation to try re-creating them and fail.

        :default: true
        '''
        result = self._values.get("prefix_stack_id_with_project_name")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def slack_notifications(self) -> typing.Optional["SlackNotifications"]:
        '''Configuration for Slack notifications.

        Requires configuring AWS Chatbot client manually first.
        '''
        result = self._values.get("slack_notifications")
        return typing.cast(typing.Optional["SlackNotifications"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="opinionated-ci-pipeline.BuildCommands",
    jsii_struct_bases=[],
    name_mapping={
        "build_and_test": "buildAndTest",
        "deploy_environment": "deployEnvironment",
        "destroy_environment": "destroyEnvironment",
        "install": "install",
        "post_deploy_environment": "postDeployEnvironment",
        "post_destroy_environment": "postDestroyEnvironment",
        "pre_deploy_environment": "preDeployEnvironment",
        "pre_destroy_environment": "preDestroyEnvironment",
        "pre_install": "preInstall",
        "synth_pipeline": "synthPipeline",
    },
)
class BuildCommands:
    def __init__(
        self,
        *,
        build_and_test: typing.Optional[typing.Sequence[builtins.str]] = None,
        deploy_environment: typing.Optional[typing.Sequence[builtins.str]] = None,
        destroy_environment: typing.Optional[typing.Sequence[builtins.str]] = None,
        install: typing.Optional[typing.Sequence[builtins.str]] = None,
        post_deploy_environment: typing.Optional[typing.Sequence[builtins.str]] = None,
        post_destroy_environment: typing.Optional[typing.Sequence[builtins.str]] = None,
        pre_deploy_environment: typing.Optional[typing.Sequence[builtins.str]] = None,
        pre_destroy_environment: typing.Optional[typing.Sequence[builtins.str]] = None,
        pre_install: typing.Optional[typing.Sequence[builtins.str]] = None,
        synth_pipeline: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param build_and_test: Executed after ``install`` in the Build step and feature branch deployment.
        :param deploy_environment: Executed after ``preDeployEnvironment`` in the feature branch deployment. By default, deploys all CDK app stacks to the environment.
        :param destroy_environment: Executed after ``preDestroyEnvironment`` in the feature branch destruction.
        :param install: Executed after ``preInstall`` in the Build step and feature branch deployment and destruction. By default, installs ``aws-cdk@2`` globally and ``npm`` or ``pnpm`` dependencies if ``packageManager`` is set.
        :param post_deploy_environment: Executed after ``deployEnvironment`` in the feature branch deployment.
        :param post_destroy_environment: Executed after ``destroyEnvironment`` in the feature branch destruction.
        :param pre_deploy_environment: Executed after ``buildAndTest`` in the feature branch deployment.
        :param pre_destroy_environment: Executed after ``install`` in the feature branch destruction.
        :param pre_install: Executed at the beginning of the Build step and feature branch deployment and destruction.
        :param synth_pipeline: Executed after the Build step. By default, synths the CDK app.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__784009b669b30e314c38fdf9a7262dc95229d2370f3ae7a3bda7d6cf264f0c25)
            check_type(argname="argument build_and_test", value=build_and_test, expected_type=type_hints["build_and_test"])
            check_type(argname="argument deploy_environment", value=deploy_environment, expected_type=type_hints["deploy_environment"])
            check_type(argname="argument destroy_environment", value=destroy_environment, expected_type=type_hints["destroy_environment"])
            check_type(argname="argument install", value=install, expected_type=type_hints["install"])
            check_type(argname="argument post_deploy_environment", value=post_deploy_environment, expected_type=type_hints["post_deploy_environment"])
            check_type(argname="argument post_destroy_environment", value=post_destroy_environment, expected_type=type_hints["post_destroy_environment"])
            check_type(argname="argument pre_deploy_environment", value=pre_deploy_environment, expected_type=type_hints["pre_deploy_environment"])
            check_type(argname="argument pre_destroy_environment", value=pre_destroy_environment, expected_type=type_hints["pre_destroy_environment"])
            check_type(argname="argument pre_install", value=pre_install, expected_type=type_hints["pre_install"])
            check_type(argname="argument synth_pipeline", value=synth_pipeline, expected_type=type_hints["synth_pipeline"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if build_and_test is not None:
            self._values["build_and_test"] = build_and_test
        if deploy_environment is not None:
            self._values["deploy_environment"] = deploy_environment
        if destroy_environment is not None:
            self._values["destroy_environment"] = destroy_environment
        if install is not None:
            self._values["install"] = install
        if post_deploy_environment is not None:
            self._values["post_deploy_environment"] = post_deploy_environment
        if post_destroy_environment is not None:
            self._values["post_destroy_environment"] = post_destroy_environment
        if pre_deploy_environment is not None:
            self._values["pre_deploy_environment"] = pre_deploy_environment
        if pre_destroy_environment is not None:
            self._values["pre_destroy_environment"] = pre_destroy_environment
        if pre_install is not None:
            self._values["pre_install"] = pre_install
        if synth_pipeline is not None:
            self._values["synth_pipeline"] = synth_pipeline

    @builtins.property
    def build_and_test(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Executed after ``install`` in the Build step and feature branch deployment.'''
        result = self._values.get("build_and_test")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deploy_environment(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Executed after ``preDeployEnvironment`` in the feature branch deployment.

        By default, deploys all CDK app stacks to the environment.
        '''
        result = self._values.get("deploy_environment")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def destroy_environment(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Executed after ``preDestroyEnvironment`` in the feature branch destruction.'''
        result = self._values.get("destroy_environment")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def install(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Executed after ``preInstall`` in the Build step and feature branch deployment and destruction.

        By default, installs ``aws-cdk@2`` globally and ``npm`` or ``pnpm`` dependencies if ``packageManager`` is set.
        '''
        result = self._values.get("install")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def post_deploy_environment(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Executed after ``deployEnvironment`` in the feature branch deployment.'''
        result = self._values.get("post_deploy_environment")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def post_destroy_environment(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Executed after ``destroyEnvironment`` in the feature branch destruction.'''
        result = self._values.get("post_destroy_environment")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pre_deploy_environment(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Executed after ``buildAndTest`` in the feature branch deployment.'''
        result = self._values.get("pre_deploy_environment")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pre_destroy_environment(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Executed after ``install`` in the feature branch destruction.'''
        result = self._values.get("pre_destroy_environment")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pre_install(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Executed at the beginning of the Build step and feature branch deployment and destruction.'''
        result = self._values.get("pre_install")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def synth_pipeline(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Executed after the Build step.

        By default, synths the CDK app.
        '''
        result = self._values.get("synth_pipeline")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildCommands(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CDKApplication(
    _aws_cdk_ceddda9d.App,
    metaclass=jsii.JSIIMeta,
    jsii_type="opinionated-ci-pipeline.CDKApplication",
):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        auto_synth: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        default_stack_synthesizer: typing.Optional[_aws_cdk_ceddda9d.IReusableStackSynthesizer] = None,
        outdir: typing.Optional[builtins.str] = None,
        policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
        post_cli_context: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        stack_traces: typing.Optional[builtins.bool] = None,
        tree_metadata: typing.Optional[builtins.bool] = None,
        pipeline: typing.Sequence[typing.Union[typing.Union["WaveDeployment", typing.Dict[builtins.str, typing.Any]], typing.Union["EnvironmentDeployment", typing.Dict[builtins.str, typing.Any]]]],
        repository: typing.Union["RepositoryProps", typing.Dict[builtins.str, typing.Any]],
        stacks: "IStacksCreation",
        cdk_output_directory: typing.Optional[builtins.str] = None,
        code_build: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        code_pipeline: typing.Optional[typing.Union["CodePipelineOverrides", typing.Dict[builtins.str, typing.Any]]] = None,
        commands: typing.Optional[typing.Union[BuildCommands, typing.Dict[builtins.str, typing.Any]]] = None,
        fix_paths_metadata: typing.Optional[builtins.bool] = None,
        package_manager: typing.Optional[builtins.str] = None,
        prefix_stack_id_with_project_name: typing.Optional[builtins.bool] = None,
        slack_notifications: typing.Optional[typing.Union["SlackNotifications", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param analytics_reporting: Include runtime versioning information in the Stacks of this app. Default: Value of 'aws:cdk:version-reporting' context key
        :param auto_synth: Automatically call ``synth()`` before the program exits. If you set this, you don't have to call ``synth()`` explicitly. Note that this feature is only available for certain programming languages, and calling ``synth()`` is still recommended. Default: true if running via CDK CLI (``CDK_OUTDIR`` is set), ``false`` otherwise
        :param context: Additional context values for the application. Context set by the CLI or the ``context`` key in ``cdk.json`` has precedence. Context can be read from any construct using ``node.getContext(key)``. Default: - no additional context
        :param default_stack_synthesizer: The stack synthesizer to use by default for all Stacks in the App. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. Default: - A ``DefaultStackSynthesizer`` with default settings
        :param outdir: The output directory into which to emit synthesized artifacts. You should never need to set this value. By default, the value you pass to the CLI's ``--output`` flag will be used, and if you change it to a different directory the CLI will fail to pick up the generated Cloud Assembly. This property is intended for internal and testing use. Default: - If this value is *not* set, considers the environment variable ``CDK_OUTDIR``. If ``CDK_OUTDIR`` is not defined, uses a temp directory.
        :param policy_validation_beta1: Validation plugins to run after synthesis. Default: - no validation plugins
        :param post_cli_context: Additional context values for the application. Context provided here has precedence over context set by: - The CLI via --context - The ``context`` key in ``cdk.json`` - The ``AppProps.context`` property This property is recommended over the ``AppProps.context`` property since you can make final decision over which context value to take in your app. Context can be read from any construct using ``node.getContext(key)``. Default: - no additional context
        :param stack_traces: Include construct creation stack trace in the ``aws:cdk:trace`` metadata key of all constructs. Default: true stack traces are included unless ``aws:cdk:disable-stack-trace`` is set in the context.
        :param tree_metadata: Include construct tree metadata as part of the Cloud Assembly. Default: true
        :param pipeline: CodePipeline deployment pipeline for the main repository branch. Can contain environments to deploy and waves that deploy multiple environments in parallel. Each environment and wave can have pre and post commands that will be executed before and after the environment or wave deployment.
        :param repository: 
        :param stacks: An object with a create() method to create Stacks for the application. The same Stacks will be deployed with main pipeline, feature-branch builds, and local deployments.
        :param cdk_output_directory: The location where CDK outputs synthetized files. Corresponds to the CDK Pipelines ShellStepProps#primaryOutputDirectory. Default: cdk.out
        :param code_build: Override CodeBuild properties, used for the main pipeline Build step as well as feature branch ephemeral environments deploys and destroys. Default: 1 hour timeout, compute type MEDIUM with Linux build image Standard 7.0
        :param code_pipeline: Override CodePipeline properties. Default: Don't use change sets
        :param commands: Commands executed to build and deploy the application.
        :param fix_paths_metadata: Whether to remove the CI resources from the beginning of the aws:cdk:path metadata. Enabling it results in the same tree view in the CloudFormation Console as with manual deployment though the CLI. Without it, the tree view for the stacks deployed through the CI starts with the 3 extra levels. This also prevents updating all resources just to change their metadata when deploying the stack alternately from the CI and CLI. This DOES NOT change the paths themselves, only the metadata. The resources that use the full path in their logical IDs (like the ``EventSourceMapping`` created with ``lambda.addEventSource()``) will still change. Default: false
        :param package_manager: Package manager used in the repository. If provided, the install commands will be set to install dependencies using given package manager.
        :param prefix_stack_id_with_project_name: Whether to prefix the CI Stack Construct ID with the project name. Prefixing assures the ID is unique, required in projects deploying multiple CI Pipelines. No-prefixing is for backwards compatibility with existing projects, where changing the Construct ID of the CI Stack would change the Logical IDs of some constructs (like Lambda EventSourceMapping, API Gateway ApiMapping) causing CloudFormation to try re-creating them and fail. Default: true
        :param slack_notifications: Configuration for Slack notifications. Requires configuring AWS Chatbot client manually first.
        '''
        props = CDKApplicationProps(
            analytics_reporting=analytics_reporting,
            auto_synth=auto_synth,
            context=context,
            default_stack_synthesizer=default_stack_synthesizer,
            outdir=outdir,
            policy_validation_beta1=policy_validation_beta1,
            post_cli_context=post_cli_context,
            stack_traces=stack_traces,
            tree_metadata=tree_metadata,
            pipeline=pipeline,
            repository=repository,
            stacks=stacks,
            cdk_output_directory=cdk_output_directory,
            code_build=code_build,
            code_pipeline=code_pipeline,
            commands=commands,
            fix_paths_metadata=fix_paths_metadata,
            package_manager=package_manager,
            prefix_stack_id_with_project_name=prefix_stack_id_with_project_name,
            slack_notifications=slack_notifications,
        )

        jsii.create(self.__class__, self, [props])


@jsii.data_type(
    jsii_type="opinionated-ci-pipeline.CDKApplicationProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.AppProps, ApplicationProps],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "auto_synth": "autoSynth",
        "context": "context",
        "default_stack_synthesizer": "defaultStackSynthesizer",
        "outdir": "outdir",
        "policy_validation_beta1": "policyValidationBeta1",
        "post_cli_context": "postCliContext",
        "stack_traces": "stackTraces",
        "tree_metadata": "treeMetadata",
        "pipeline": "pipeline",
        "repository": "repository",
        "stacks": "stacks",
        "cdk_output_directory": "cdkOutputDirectory",
        "code_build": "codeBuild",
        "code_pipeline": "codePipeline",
        "commands": "commands",
        "fix_paths_metadata": "fixPathsMetadata",
        "package_manager": "packageManager",
        "prefix_stack_id_with_project_name": "prefixStackIdWithProjectName",
        "slack_notifications": "slackNotifications",
    },
)
class CDKApplicationProps(_aws_cdk_ceddda9d.AppProps, ApplicationProps):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        auto_synth: typing.Optional[builtins.bool] = None,
        context: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        default_stack_synthesizer: typing.Optional[_aws_cdk_ceddda9d.IReusableStackSynthesizer] = None,
        outdir: typing.Optional[builtins.str] = None,
        policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
        post_cli_context: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        stack_traces: typing.Optional[builtins.bool] = None,
        tree_metadata: typing.Optional[builtins.bool] = None,
        pipeline: typing.Sequence[typing.Union[typing.Union["WaveDeployment", typing.Dict[builtins.str, typing.Any]], typing.Union["EnvironmentDeployment", typing.Dict[builtins.str, typing.Any]]]],
        repository: typing.Union["RepositoryProps", typing.Dict[builtins.str, typing.Any]],
        stacks: "IStacksCreation",
        cdk_output_directory: typing.Optional[builtins.str] = None,
        code_build: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        code_pipeline: typing.Optional[typing.Union["CodePipelineOverrides", typing.Dict[builtins.str, typing.Any]]] = None,
        commands: typing.Optional[typing.Union[BuildCommands, typing.Dict[builtins.str, typing.Any]]] = None,
        fix_paths_metadata: typing.Optional[builtins.bool] = None,
        package_manager: typing.Optional[builtins.str] = None,
        prefix_stack_id_with_project_name: typing.Optional[builtins.bool] = None,
        slack_notifications: typing.Optional[typing.Union["SlackNotifications", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param analytics_reporting: Include runtime versioning information in the Stacks of this app. Default: Value of 'aws:cdk:version-reporting' context key
        :param auto_synth: Automatically call ``synth()`` before the program exits. If you set this, you don't have to call ``synth()`` explicitly. Note that this feature is only available for certain programming languages, and calling ``synth()`` is still recommended. Default: true if running via CDK CLI (``CDK_OUTDIR`` is set), ``false`` otherwise
        :param context: Additional context values for the application. Context set by the CLI or the ``context`` key in ``cdk.json`` has precedence. Context can be read from any construct using ``node.getContext(key)``. Default: - no additional context
        :param default_stack_synthesizer: The stack synthesizer to use by default for all Stacks in the App. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. Default: - A ``DefaultStackSynthesizer`` with default settings
        :param outdir: The output directory into which to emit synthesized artifacts. You should never need to set this value. By default, the value you pass to the CLI's ``--output`` flag will be used, and if you change it to a different directory the CLI will fail to pick up the generated Cloud Assembly. This property is intended for internal and testing use. Default: - If this value is *not* set, considers the environment variable ``CDK_OUTDIR``. If ``CDK_OUTDIR`` is not defined, uses a temp directory.
        :param policy_validation_beta1: Validation plugins to run after synthesis. Default: - no validation plugins
        :param post_cli_context: Additional context values for the application. Context provided here has precedence over context set by: - The CLI via --context - The ``context`` key in ``cdk.json`` - The ``AppProps.context`` property This property is recommended over the ``AppProps.context`` property since you can make final decision over which context value to take in your app. Context can be read from any construct using ``node.getContext(key)``. Default: - no additional context
        :param stack_traces: Include construct creation stack trace in the ``aws:cdk:trace`` metadata key of all constructs. Default: true stack traces are included unless ``aws:cdk:disable-stack-trace`` is set in the context.
        :param tree_metadata: Include construct tree metadata as part of the Cloud Assembly. Default: true
        :param pipeline: CodePipeline deployment pipeline for the main repository branch. Can contain environments to deploy and waves that deploy multiple environments in parallel. Each environment and wave can have pre and post commands that will be executed before and after the environment or wave deployment.
        :param repository: 
        :param stacks: An object with a create() method to create Stacks for the application. The same Stacks will be deployed with main pipeline, feature-branch builds, and local deployments.
        :param cdk_output_directory: The location where CDK outputs synthetized files. Corresponds to the CDK Pipelines ShellStepProps#primaryOutputDirectory. Default: cdk.out
        :param code_build: Override CodeBuild properties, used for the main pipeline Build step as well as feature branch ephemeral environments deploys and destroys. Default: 1 hour timeout, compute type MEDIUM with Linux build image Standard 7.0
        :param code_pipeline: Override CodePipeline properties. Default: Don't use change sets
        :param commands: Commands executed to build and deploy the application.
        :param fix_paths_metadata: Whether to remove the CI resources from the beginning of the aws:cdk:path metadata. Enabling it results in the same tree view in the CloudFormation Console as with manual deployment though the CLI. Without it, the tree view for the stacks deployed through the CI starts with the 3 extra levels. This also prevents updating all resources just to change their metadata when deploying the stack alternately from the CI and CLI. This DOES NOT change the paths themselves, only the metadata. The resources that use the full path in their logical IDs (like the ``EventSourceMapping`` created with ``lambda.addEventSource()``) will still change. Default: false
        :param package_manager: Package manager used in the repository. If provided, the install commands will be set to install dependencies using given package manager.
        :param prefix_stack_id_with_project_name: Whether to prefix the CI Stack Construct ID with the project name. Prefixing assures the ID is unique, required in projects deploying multiple CI Pipelines. No-prefixing is for backwards compatibility with existing projects, where changing the Construct ID of the CI Stack would change the Logical IDs of some constructs (like Lambda EventSourceMapping, API Gateway ApiMapping) causing CloudFormation to try re-creating them and fail. Default: true
        :param slack_notifications: Configuration for Slack notifications. Requires configuring AWS Chatbot client manually first.
        '''
        if isinstance(repository, dict):
            repository = RepositoryProps(**repository)
        if isinstance(code_build, dict):
            code_build = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(**code_build)
        if isinstance(code_pipeline, dict):
            code_pipeline = CodePipelineOverrides(**code_pipeline)
        if isinstance(commands, dict):
            commands = BuildCommands(**commands)
        if isinstance(slack_notifications, dict):
            slack_notifications = SlackNotifications(**slack_notifications)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be38be79ae4e169cdad1ff5fa548afd5af816580eaf5ec1eca5799f6bf3ace32)
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument auto_synth", value=auto_synth, expected_type=type_hints["auto_synth"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
            check_type(argname="argument default_stack_synthesizer", value=default_stack_synthesizer, expected_type=type_hints["default_stack_synthesizer"])
            check_type(argname="argument outdir", value=outdir, expected_type=type_hints["outdir"])
            check_type(argname="argument policy_validation_beta1", value=policy_validation_beta1, expected_type=type_hints["policy_validation_beta1"])
            check_type(argname="argument post_cli_context", value=post_cli_context, expected_type=type_hints["post_cli_context"])
            check_type(argname="argument stack_traces", value=stack_traces, expected_type=type_hints["stack_traces"])
            check_type(argname="argument tree_metadata", value=tree_metadata, expected_type=type_hints["tree_metadata"])
            check_type(argname="argument pipeline", value=pipeline, expected_type=type_hints["pipeline"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument stacks", value=stacks, expected_type=type_hints["stacks"])
            check_type(argname="argument cdk_output_directory", value=cdk_output_directory, expected_type=type_hints["cdk_output_directory"])
            check_type(argname="argument code_build", value=code_build, expected_type=type_hints["code_build"])
            check_type(argname="argument code_pipeline", value=code_pipeline, expected_type=type_hints["code_pipeline"])
            check_type(argname="argument commands", value=commands, expected_type=type_hints["commands"])
            check_type(argname="argument fix_paths_metadata", value=fix_paths_metadata, expected_type=type_hints["fix_paths_metadata"])
            check_type(argname="argument package_manager", value=package_manager, expected_type=type_hints["package_manager"])
            check_type(argname="argument prefix_stack_id_with_project_name", value=prefix_stack_id_with_project_name, expected_type=type_hints["prefix_stack_id_with_project_name"])
            check_type(argname="argument slack_notifications", value=slack_notifications, expected_type=type_hints["slack_notifications"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "pipeline": pipeline,
            "repository": repository,
            "stacks": stacks,
        }
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if auto_synth is not None:
            self._values["auto_synth"] = auto_synth
        if context is not None:
            self._values["context"] = context
        if default_stack_synthesizer is not None:
            self._values["default_stack_synthesizer"] = default_stack_synthesizer
        if outdir is not None:
            self._values["outdir"] = outdir
        if policy_validation_beta1 is not None:
            self._values["policy_validation_beta1"] = policy_validation_beta1
        if post_cli_context is not None:
            self._values["post_cli_context"] = post_cli_context
        if stack_traces is not None:
            self._values["stack_traces"] = stack_traces
        if tree_metadata is not None:
            self._values["tree_metadata"] = tree_metadata
        if cdk_output_directory is not None:
            self._values["cdk_output_directory"] = cdk_output_directory
        if code_build is not None:
            self._values["code_build"] = code_build
        if code_pipeline is not None:
            self._values["code_pipeline"] = code_pipeline
        if commands is not None:
            self._values["commands"] = commands
        if fix_paths_metadata is not None:
            self._values["fix_paths_metadata"] = fix_paths_metadata
        if package_manager is not None:
            self._values["package_manager"] = package_manager
        if prefix_stack_id_with_project_name is not None:
            self._values["prefix_stack_id_with_project_name"] = prefix_stack_id_with_project_name
        if slack_notifications is not None:
            self._values["slack_notifications"] = slack_notifications

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in the Stacks of this app.

        :default: Value of 'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_synth(self) -> typing.Optional[builtins.bool]:
        '''Automatically call ``synth()`` before the program exits.

        If you set this, you don't have to call ``synth()`` explicitly. Note that
        this feature is only available for certain programming languages, and
        calling ``synth()`` is still recommended.

        :default:

        true if running via CDK CLI (``CDK_OUTDIR`` is set), ``false``
        otherwise
        '''
        result = self._values.get("auto_synth")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def context(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Additional context values for the application.

        Context set by the CLI or the ``context`` key in ``cdk.json`` has precedence.

        Context can be read from any construct using ``node.getContext(key)``.

        :default: - no additional context
        '''
        result = self._values.get("context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def default_stack_synthesizer(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.IReusableStackSynthesizer]:
        '''The stack synthesizer to use by default for all Stacks in the App.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        :default: - A ``DefaultStackSynthesizer`` with default settings
        '''
        result = self._values.get("default_stack_synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IReusableStackSynthesizer], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''The output directory into which to emit synthesized artifacts.

        You should never need to set this value. By default, the value you pass to
        the CLI's ``--output`` flag will be used, and if you change it to a different
        directory the CLI will fail to pick up the generated Cloud Assembly.

        This property is intended for internal and testing use.

        :default:

        - If this value is *not* set, considers the environment variable ``CDK_OUTDIR``.
        If ``CDK_OUTDIR`` is not defined, uses a temp directory.
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_validation_beta1(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]]:
        '''Validation plugins to run after synthesis.

        :default: - no validation plugins
        '''
        result = self._values.get("policy_validation_beta1")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]], result)

    @builtins.property
    def post_cli_context(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Additional context values for the application.

        Context provided here has precedence over context set by:

        - The CLI via --context
        - The ``context`` key in ``cdk.json``
        - The ``AppProps.context`` property

        This property is recommended over the ``AppProps.context`` property since you
        can make final decision over which context value to take in your app.

        Context can be read from any construct using ``node.getContext(key)``.

        :default: - no additional context

        Example::

            // context from the CLI and from `cdk.json` are stored in the
            // CDK_CONTEXT env variable
            const cliContext = JSON.parse(process.env.CDK_CONTEXT!);
            
            // determine whether to take the context passed in the CLI or not
            const determineValue = process.env.PROD ? cliContext.SOMEKEY : 'my-prod-value';
            new App({
              postCliContext: {
                SOMEKEY: determineValue,
              },
            });
        '''
        result = self._values.get("post_cli_context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def stack_traces(self) -> typing.Optional[builtins.bool]:
        '''Include construct creation stack trace in the ``aws:cdk:trace`` metadata key of all constructs.

        :default: true stack traces are included unless ``aws:cdk:disable-stack-trace`` is set in the context.
        '''
        result = self._values.get("stack_traces")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def tree_metadata(self) -> typing.Optional[builtins.bool]:
        '''Include construct tree metadata as part of the Cloud Assembly.

        :default: true
        '''
        result = self._values.get("tree_metadata")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pipeline(
        self,
    ) -> typing.List[typing.Union["WaveDeployment", "EnvironmentDeployment"]]:
        '''CodePipeline deployment pipeline for the main repository branch.

        Can contain environments to deploy
        and waves that deploy multiple environments in parallel.

        Each environment and wave can have pre and post commands
        that will be executed before and after the environment or wave deployment.
        '''
        result = self._values.get("pipeline")
        assert result is not None, "Required property 'pipeline' is missing"
        return typing.cast(typing.List[typing.Union["WaveDeployment", "EnvironmentDeployment"]], result)

    @builtins.property
    def repository(self) -> "RepositoryProps":
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast("RepositoryProps", result)

    @builtins.property
    def stacks(self) -> "IStacksCreation":
        '''An object with a create() method to create Stacks for the application.

        The same Stacks will be deployed with main pipeline, feature-branch builds, and local deployments.
        '''
        result = self._values.get("stacks")
        assert result is not None, "Required property 'stacks' is missing"
        return typing.cast("IStacksCreation", result)

    @builtins.property
    def cdk_output_directory(self) -> typing.Optional[builtins.str]:
        '''The location where CDK outputs synthetized files.

        Corresponds to the CDK Pipelines ShellStepProps#primaryOutputDirectory.

        :default: cdk.out
        '''
        result = self._values.get("cdk_output_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def code_build(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions]:
        '''Override CodeBuild properties, used for the main pipeline Build step as well as feature branch ephemeral environments deploys and destroys.

        :default: 1 hour timeout, compute type MEDIUM with Linux build image Standard 7.0
        '''
        result = self._values.get("code_build")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions], result)

    @builtins.property
    def code_pipeline(self) -> typing.Optional["CodePipelineOverrides"]:
        '''Override CodePipeline properties.

        :default: Don't use change sets
        '''
        result = self._values.get("code_pipeline")
        return typing.cast(typing.Optional["CodePipelineOverrides"], result)

    @builtins.property
    def commands(self) -> typing.Optional[BuildCommands]:
        '''Commands executed to build and deploy the application.'''
        result = self._values.get("commands")
        return typing.cast(typing.Optional[BuildCommands], result)

    @builtins.property
    def fix_paths_metadata(self) -> typing.Optional[builtins.bool]:
        '''Whether to remove the CI resources from the beginning of the aws:cdk:path metadata.

        Enabling it results in the same tree view in the CloudFormation Console as with manual deployment though the CLI.
        Without it, the tree view for the stacks deployed through the CI starts with the 3 extra levels.

        This also prevents updating all resources just to change their metadata
        when deploying the stack alternately from the CI and CLI.

        This DOES NOT change the paths themselves, only the metadata.
        The resources that use the full path in their logical IDs
        (like the ``EventSourceMapping`` created with ``lambda.addEventSource()``) will still change.

        :default: false
        '''
        result = self._values.get("fix_paths_metadata")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def package_manager(self) -> typing.Optional[builtins.str]:
        '''Package manager used in the repository.

        If provided, the install commands will be set to install dependencies using given package manager.
        '''
        result = self._values.get("package_manager")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix_stack_id_with_project_name(self) -> typing.Optional[builtins.bool]:
        '''Whether to prefix the CI Stack Construct ID with the project name.

        Prefixing assures the ID is unique, required in projects deploying multiple CI Pipelines.

        No-prefixing is for backwards compatibility with existing projects,
        where changing the Construct ID of the CI Stack would change the Logical IDs of some constructs
        (like Lambda EventSourceMapping, API Gateway ApiMapping)
        causing CloudFormation to try re-creating them and fail.

        :default: true
        '''
        result = self._values.get("prefix_stack_id_with_project_name")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def slack_notifications(self) -> typing.Optional["SlackNotifications"]:
        '''Configuration for Slack notifications.

        Requires configuring AWS Chatbot client manually first.
        '''
        result = self._values.get("slack_notifications")
        return typing.cast(typing.Optional["SlackNotifications"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CDKApplicationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="opinionated-ci-pipeline.CodePipelineOverrides",
    jsii_struct_bases=[],
    name_mapping={
        "asset_publishing_code_build_defaults": "assetPublishingCodeBuildDefaults",
        "code_build_defaults": "codeBuildDefaults",
        "docker_credentials": "dockerCredentials",
        "docker_enabled_for_self_mutation": "dockerEnabledForSelfMutation",
        "docker_enabled_for_synth": "dockerEnabledForSynth",
        "enable_key_rotation": "enableKeyRotation",
        "pipeline_name": "pipelineName",
        "publish_assets_in_parallel": "publishAssetsInParallel",
        "reuse_cross_region_support_stacks": "reuseCrossRegionSupportStacks",
        "role": "role",
        "self_mutation": "selfMutation",
        "self_mutation_code_build_defaults": "selfMutationCodeBuildDefaults",
        "synth_code_build_defaults": "synthCodeBuildDefaults",
        "use_change_sets": "useChangeSets",
    },
)
class CodePipelineOverrides:
    def __init__(
        self,
        *,
        asset_publishing_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        docker_credentials: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.DockerCredential]] = None,
        docker_enabled_for_self_mutation: typing.Optional[builtins.bool] = None,
        docker_enabled_for_synth: typing.Optional[builtins.bool] = None,
        enable_key_rotation: typing.Optional[builtins.bool] = None,
        pipeline_name: typing.Optional[builtins.str] = None,
        publish_assets_in_parallel: typing.Optional[builtins.bool] = None,
        reuse_cross_region_support_stacks: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        self_mutation: typing.Optional[builtins.bool] = None,
        self_mutation_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        synth_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        use_change_sets: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Since jsii does not support Partial or Omit, we have to define all properties from CodePipelineProps that may be overriden manually.

        :param asset_publishing_code_build_defaults: 
        :param code_build_defaults: 
        :param docker_credentials: 
        :param docker_enabled_for_self_mutation: 
        :param docker_enabled_for_synth: 
        :param enable_key_rotation: 
        :param pipeline_name: 
        :param publish_assets_in_parallel: 
        :param reuse_cross_region_support_stacks: 
        :param role: 
        :param self_mutation: 
        :param self_mutation_code_build_defaults: 
        :param synth_code_build_defaults: 
        :param use_change_sets: 
        '''
        if isinstance(asset_publishing_code_build_defaults, dict):
            asset_publishing_code_build_defaults = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(**asset_publishing_code_build_defaults)
        if isinstance(code_build_defaults, dict):
            code_build_defaults = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(**code_build_defaults)
        if isinstance(self_mutation_code_build_defaults, dict):
            self_mutation_code_build_defaults = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(**self_mutation_code_build_defaults)
        if isinstance(synth_code_build_defaults, dict):
            synth_code_build_defaults = _aws_cdk_pipelines_ceddda9d.CodeBuildOptions(**synth_code_build_defaults)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7bac62224aec74b6d37f678f5bdede0184616abc1fb2eafb3a4aa19f1c20fd4)
            check_type(argname="argument asset_publishing_code_build_defaults", value=asset_publishing_code_build_defaults, expected_type=type_hints["asset_publishing_code_build_defaults"])
            check_type(argname="argument code_build_defaults", value=code_build_defaults, expected_type=type_hints["code_build_defaults"])
            check_type(argname="argument docker_credentials", value=docker_credentials, expected_type=type_hints["docker_credentials"])
            check_type(argname="argument docker_enabled_for_self_mutation", value=docker_enabled_for_self_mutation, expected_type=type_hints["docker_enabled_for_self_mutation"])
            check_type(argname="argument docker_enabled_for_synth", value=docker_enabled_for_synth, expected_type=type_hints["docker_enabled_for_synth"])
            check_type(argname="argument enable_key_rotation", value=enable_key_rotation, expected_type=type_hints["enable_key_rotation"])
            check_type(argname="argument pipeline_name", value=pipeline_name, expected_type=type_hints["pipeline_name"])
            check_type(argname="argument publish_assets_in_parallel", value=publish_assets_in_parallel, expected_type=type_hints["publish_assets_in_parallel"])
            check_type(argname="argument reuse_cross_region_support_stacks", value=reuse_cross_region_support_stacks, expected_type=type_hints["reuse_cross_region_support_stacks"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument self_mutation", value=self_mutation, expected_type=type_hints["self_mutation"])
            check_type(argname="argument self_mutation_code_build_defaults", value=self_mutation_code_build_defaults, expected_type=type_hints["self_mutation_code_build_defaults"])
            check_type(argname="argument synth_code_build_defaults", value=synth_code_build_defaults, expected_type=type_hints["synth_code_build_defaults"])
            check_type(argname="argument use_change_sets", value=use_change_sets, expected_type=type_hints["use_change_sets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if asset_publishing_code_build_defaults is not None:
            self._values["asset_publishing_code_build_defaults"] = asset_publishing_code_build_defaults
        if code_build_defaults is not None:
            self._values["code_build_defaults"] = code_build_defaults
        if docker_credentials is not None:
            self._values["docker_credentials"] = docker_credentials
        if docker_enabled_for_self_mutation is not None:
            self._values["docker_enabled_for_self_mutation"] = docker_enabled_for_self_mutation
        if docker_enabled_for_synth is not None:
            self._values["docker_enabled_for_synth"] = docker_enabled_for_synth
        if enable_key_rotation is not None:
            self._values["enable_key_rotation"] = enable_key_rotation
        if pipeline_name is not None:
            self._values["pipeline_name"] = pipeline_name
        if publish_assets_in_parallel is not None:
            self._values["publish_assets_in_parallel"] = publish_assets_in_parallel
        if reuse_cross_region_support_stacks is not None:
            self._values["reuse_cross_region_support_stacks"] = reuse_cross_region_support_stacks
        if role is not None:
            self._values["role"] = role
        if self_mutation is not None:
            self._values["self_mutation"] = self_mutation
        if self_mutation_code_build_defaults is not None:
            self._values["self_mutation_code_build_defaults"] = self_mutation_code_build_defaults
        if synth_code_build_defaults is not None:
            self._values["synth_code_build_defaults"] = synth_code_build_defaults
        if use_change_sets is not None:
            self._values["use_change_sets"] = use_change_sets

    @builtins.property
    def asset_publishing_code_build_defaults(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions]:
        result = self._values.get("asset_publishing_code_build_defaults")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions], result)

    @builtins.property
    def code_build_defaults(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions]:
        result = self._values.get("code_build_defaults")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions], result)

    @builtins.property
    def docker_credentials(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_pipelines_ceddda9d.DockerCredential]]:
        result = self._values.get("docker_credentials")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_pipelines_ceddda9d.DockerCredential]], result)

    @builtins.property
    def docker_enabled_for_self_mutation(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("docker_enabled_for_self_mutation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docker_enabled_for_synth(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("docker_enabled_for_synth")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_key_rotation(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enable_key_rotation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pipeline_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("pipeline_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish_assets_in_parallel(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("publish_assets_in_parallel")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def reuse_cross_region_support_stacks(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("reuse_cross_region_support_stacks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def self_mutation(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("self_mutation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def self_mutation_code_build_defaults(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions]:
        result = self._values.get("self_mutation_code_build_defaults")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions], result)

    @builtins.property
    def synth_code_build_defaults(
        self,
    ) -> typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions]:
        result = self._values.get("synth_code_build_defaults")
        return typing.cast(typing.Optional[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions], result)

    @builtins.property
    def use_change_sets(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("use_change_sets")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodePipelineOverrides(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="opinionated-ci-pipeline.EnvironmentDeployment",
    jsii_struct_bases=[],
    name_mapping={
        "environment": "environment",
        "manual_approval": "manualApproval",
        "post": "post",
        "pre": "pre",
    },
)
class EnvironmentDeployment:
    def __init__(
        self,
        *,
        environment: builtins.str,
        manual_approval: typing.Optional[builtins.bool] = None,
        post: typing.Optional[typing.Sequence[builtins.str]] = None,
        pre: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param environment: Environment name. Environment will be deployed to AWS account and region defined in cdk.json file ``context/environments`` properties, falling back to the ``default`` environment settings if given environment configuration is not found.
        :param manual_approval: Flag indicating whether environment deployment requires manual approval.
        :param post: Commands to execute after the environment deployment.
        :param pre: Commands to execute before the environment deployment.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a56d8f8652385a6beef9373eed0946aec4a1e2ca901b17252542af97a91c99a)
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument manual_approval", value=manual_approval, expected_type=type_hints["manual_approval"])
            check_type(argname="argument post", value=post, expected_type=type_hints["post"])
            check_type(argname="argument pre", value=pre, expected_type=type_hints["pre"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "environment": environment,
        }
        if manual_approval is not None:
            self._values["manual_approval"] = manual_approval
        if post is not None:
            self._values["post"] = post
        if pre is not None:
            self._values["pre"] = pre

    @builtins.property
    def environment(self) -> builtins.str:
        '''Environment name.

        Environment will be deployed to AWS account and region
        defined in cdk.json file ``context/environments`` properties,
        falling back to the ``default`` environment settings if given environment configuration is not found.
        '''
        result = self._values.get("environment")
        assert result is not None, "Required property 'environment' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def manual_approval(self) -> typing.Optional[builtins.bool]:
        '''Flag indicating whether environment deployment requires manual approval.'''
        result = self._values.get("manual_approval")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def post(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Commands to execute after the environment deployment.'''
        result = self._values.get("post")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pre(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Commands to execute before the environment deployment.'''
        result = self._values.get("pre")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnvironmentDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="opinionated-ci-pipeline.IStacksCreation")
class IStacksCreation(typing_extensions.Protocol):
    '''To provide a method as parameter, jsii requires creating a behavioral interface, prefixed with "I".

    Mixing structural and behavioral interfaces is not always possible, hence we extract stacks creation
    to a separate object described by this behavioral interface.
    '''

    @jsii.member(jsii_name="create")
    def create(
        self,
        scope: _constructs_77d1e7e8.Construct,
        project_name: builtins.str,
        env_name: builtins.str,
    ) -> None:
        '''Create Stacks for the application.

        Use provided scope as stacks' parent (first constructor argument).

        Stacks must include provided environment name in their names
        to distinguish them when deploying multiple environments
        (like feature-branch environments) to the same account.

        :param scope: -
        :param project_name: -
        :param env_name: -
        '''
        ...


class _IStacksCreationProxy:
    '''To provide a method as parameter, jsii requires creating a behavioral interface, prefixed with "I".

    Mixing structural and behavioral interfaces is not always possible, hence we extract stacks creation
    to a separate object described by this behavioral interface.
    '''

    __jsii_type__: typing.ClassVar[str] = "opinionated-ci-pipeline.IStacksCreation"

    @jsii.member(jsii_name="create")
    def create(
        self,
        scope: _constructs_77d1e7e8.Construct,
        project_name: builtins.str,
        env_name: builtins.str,
    ) -> None:
        '''Create Stacks for the application.

        Use provided scope as stacks' parent (first constructor argument).

        Stacks must include provided environment name in their names
        to distinguish them when deploying multiple environments
        (like feature-branch environments) to the same account.

        :param scope: -
        :param project_name: -
        :param env_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f94daa933ae3ad6d5e4b09fd8274268c1c6c4ce67db84eea5360a505e3c5d56)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument project_name", value=project_name, expected_type=type_hints["project_name"])
            check_type(argname="argument env_name", value=env_name, expected_type=type_hints["env_name"])
        return typing.cast(None, jsii.invoke(self, "create", [scope, project_name, env_name]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStacksCreation).__jsii_proxy_class__ = lambda : _IStacksCreationProxy


@jsii.data_type(
    jsii_type="opinionated-ci-pipeline.RepositoryProps",
    jsii_struct_bases=[],
    name_mapping={
        "host": "host",
        "name": "name",
        "default_branch": "defaultBranch",
        "feature_branch_prefixes": "featureBranchPrefixes",
    },
)
class RepositoryProps:
    def __init__(
        self,
        *,
        host: builtins.str,
        name: builtins.str,
        default_branch: typing.Optional[builtins.str] = None,
        feature_branch_prefixes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param host: Repository hosting.
        :param name: Like "my-comapny/my-repo".
        :param default_branch: Branch to deploy the environments from in the main pipeline. Default: main
        :param feature_branch_prefixes: Configure the prefix branch names that should be automatically deployed as feature branches. Default: deploy all branches
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6f830ab1d423354edc601071d8aae1b0849f4eb33644f06838e41508d8ba714)
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument default_branch", value=default_branch, expected_type=type_hints["default_branch"])
            check_type(argname="argument feature_branch_prefixes", value=feature_branch_prefixes, expected_type=type_hints["feature_branch_prefixes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "host": host,
            "name": name,
        }
        if default_branch is not None:
            self._values["default_branch"] = default_branch
        if feature_branch_prefixes is not None:
            self._values["feature_branch_prefixes"] = feature_branch_prefixes

    @builtins.property
    def host(self) -> builtins.str:
        '''Repository hosting.'''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Like "my-comapny/my-repo".'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def default_branch(self) -> typing.Optional[builtins.str]:
        '''Branch to deploy the environments from in the main pipeline.

        :default: main
        '''
        result = self._values.get("default_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def feature_branch_prefixes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Configure the prefix branch names that should be automatically deployed as feature branches.

        :default: deploy all branches
        '''
        result = self._values.get("feature_branch_prefixes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="opinionated-ci-pipeline.SlackChannelConfig",
    jsii_struct_bases=[],
    name_mapping={"channel_id": "channelId", "workspace_id": "workspaceId"},
)
class SlackChannelConfig:
    def __init__(self, *, channel_id: builtins.str, workspace_id: builtins.str) -> None:
        '''
        :param channel_id: 
        :param workspace_id: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6dccc8f244e67e4c56e0d08fc41124131552dcc2c40cdde13de9d458d473882)
            check_type(argname="argument channel_id", value=channel_id, expected_type=type_hints["channel_id"])
            check_type(argname="argument workspace_id", value=workspace_id, expected_type=type_hints["workspace_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "channel_id": channel_id,
            "workspace_id": workspace_id,
        }

    @builtins.property
    def channel_id(self) -> builtins.str:
        result = self._values.get("channel_id")
        assert result is not None, "Required property 'channel_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workspace_id(self) -> builtins.str:
        result = self._values.get("workspace_id")
        assert result is not None, "Required property 'workspace_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackChannelConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="opinionated-ci-pipeline.SlackNotifications",
    jsii_struct_bases=[],
    name_mapping={
        "feature_branch_failures": "featureBranchFailures",
        "main_pipeline_failures": "mainPipelineFailures",
    },
)
class SlackNotifications:
    def __init__(
        self,
        *,
        feature_branch_failures: typing.Optional[typing.Union[SlackChannelConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        main_pipeline_failures: typing.Optional[typing.Union[SlackChannelConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param feature_branch_failures: Slack notifications configuration for feature branch deployment failures. Default: Slack notifications are not being sent
        :param main_pipeline_failures: Slack notifications configuration for main pipeline failures. Default: Slack notifications are not being sent
        '''
        if isinstance(feature_branch_failures, dict):
            feature_branch_failures = SlackChannelConfig(**feature_branch_failures)
        if isinstance(main_pipeline_failures, dict):
            main_pipeline_failures = SlackChannelConfig(**main_pipeline_failures)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62e47fdb1eef2b0738fcc2152a329dd258aee175431814841e5687481f56c87b)
            check_type(argname="argument feature_branch_failures", value=feature_branch_failures, expected_type=type_hints["feature_branch_failures"])
            check_type(argname="argument main_pipeline_failures", value=main_pipeline_failures, expected_type=type_hints["main_pipeline_failures"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if feature_branch_failures is not None:
            self._values["feature_branch_failures"] = feature_branch_failures
        if main_pipeline_failures is not None:
            self._values["main_pipeline_failures"] = main_pipeline_failures

    @builtins.property
    def feature_branch_failures(self) -> typing.Optional[SlackChannelConfig]:
        '''Slack notifications configuration for feature branch deployment failures.

        :default: Slack notifications are not being sent
        '''
        result = self._values.get("feature_branch_failures")
        return typing.cast(typing.Optional[SlackChannelConfig], result)

    @builtins.property
    def main_pipeline_failures(self) -> typing.Optional[SlackChannelConfig]:
        '''Slack notifications configuration for main pipeline failures.

        :default: Slack notifications are not being sent
        '''
        result = self._values.get("main_pipeline_failures")
        return typing.cast(typing.Optional[SlackChannelConfig], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackNotifications(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="opinionated-ci-pipeline.WaveDeployment",
    jsii_struct_bases=[],
    name_mapping={
        "environments": "environments",
        "wave": "wave",
        "manual_approval": "manualApproval",
        "post": "post",
        "post_each_environment": "postEachEnvironment",
        "pre": "pre",
        "pre_each_environment": "preEachEnvironment",
    },
)
class WaveDeployment:
    def __init__(
        self,
        *,
        environments: typing.Sequence[typing.Union[EnvironmentDeployment, typing.Dict[builtins.str, typing.Any]]],
        wave: builtins.str,
        manual_approval: typing.Optional[builtins.bool] = None,
        post: typing.Optional[typing.Sequence[builtins.str]] = None,
        post_each_environment: typing.Optional[typing.Sequence[builtins.str]] = None,
        pre: typing.Optional[typing.Sequence[builtins.str]] = None,
        pre_each_environment: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param environments: List of environments to deploy in parallel.
        :param wave: Wave name.
        :param manual_approval: Flag indicating whether environment deployment requires manual approval.
        :param post: Commands to execute after the wave deployment.
        :param post_each_environment: Commands to execute after environment deployment. If environment configuration also contains commands to execute post-deployment, they will be executed before the commands defined here.
        :param pre: Commands to execute before the wave deployment.
        :param pre_each_environment: Commands to execute before each environment deployment. If environment configuration also contains commands to execute pre-deployment, they will be executed after the commands defined here.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e2f9daf95ae58e92db6a6c5f2f46d1d02b4f767b770eaf9116fc04ca2c5158e)
            check_type(argname="argument environments", value=environments, expected_type=type_hints["environments"])
            check_type(argname="argument wave", value=wave, expected_type=type_hints["wave"])
            check_type(argname="argument manual_approval", value=manual_approval, expected_type=type_hints["manual_approval"])
            check_type(argname="argument post", value=post, expected_type=type_hints["post"])
            check_type(argname="argument post_each_environment", value=post_each_environment, expected_type=type_hints["post_each_environment"])
            check_type(argname="argument pre", value=pre, expected_type=type_hints["pre"])
            check_type(argname="argument pre_each_environment", value=pre_each_environment, expected_type=type_hints["pre_each_environment"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "environments": environments,
            "wave": wave,
        }
        if manual_approval is not None:
            self._values["manual_approval"] = manual_approval
        if post is not None:
            self._values["post"] = post
        if post_each_environment is not None:
            self._values["post_each_environment"] = post_each_environment
        if pre is not None:
            self._values["pre"] = pre
        if pre_each_environment is not None:
            self._values["pre_each_environment"] = pre_each_environment

    @builtins.property
    def environments(self) -> typing.List[EnvironmentDeployment]:
        '''List of environments to deploy in parallel.'''
        result = self._values.get("environments")
        assert result is not None, "Required property 'environments' is missing"
        return typing.cast(typing.List[EnvironmentDeployment], result)

    @builtins.property
    def wave(self) -> builtins.str:
        '''Wave name.'''
        result = self._values.get("wave")
        assert result is not None, "Required property 'wave' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def manual_approval(self) -> typing.Optional[builtins.bool]:
        '''Flag indicating whether environment deployment requires manual approval.'''
        result = self._values.get("manual_approval")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def post(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Commands to execute after the wave deployment.'''
        result = self._values.get("post")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def post_each_environment(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Commands to execute after environment deployment.

        If environment configuration also contains commands to execute post-deployment,
        they will be executed before the commands defined here.
        '''
        result = self._values.get("post_each_environment")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pre(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Commands to execute before the wave deployment.'''
        result = self._values.get("pre")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pre_each_environment(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Commands to execute before each environment deployment.

        If environment configuration also contains commands to execute pre-deployment,
        they will be executed after the commands defined here.
        '''
        result = self._values.get("pre_each_environment")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WaveDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApplicationProps",
    "BuildCommands",
    "CDKApplication",
    "CDKApplicationProps",
    "CodePipelineOverrides",
    "EnvironmentDeployment",
    "IStacksCreation",
    "RepositoryProps",
    "SlackChannelConfig",
    "SlackNotifications",
    "WaveDeployment",
]

publication.publish()

def _typecheckingstub__d22629910ce624c4144f7d3a67b45ba1c7b1018575c9f66d6177bc139efb6eb9(
    *,
    pipeline: typing.Sequence[typing.Union[typing.Union[WaveDeployment, typing.Dict[builtins.str, typing.Any]], typing.Union[EnvironmentDeployment, typing.Dict[builtins.str, typing.Any]]]],
    repository: typing.Union[RepositoryProps, typing.Dict[builtins.str, typing.Any]],
    stacks: IStacksCreation,
    cdk_output_directory: typing.Optional[builtins.str] = None,
    code_build: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    code_pipeline: typing.Optional[typing.Union[CodePipelineOverrides, typing.Dict[builtins.str, typing.Any]]] = None,
    commands: typing.Optional[typing.Union[BuildCommands, typing.Dict[builtins.str, typing.Any]]] = None,
    fix_paths_metadata: typing.Optional[builtins.bool] = None,
    package_manager: typing.Optional[builtins.str] = None,
    prefix_stack_id_with_project_name: typing.Optional[builtins.bool] = None,
    slack_notifications: typing.Optional[typing.Union[SlackNotifications, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__784009b669b30e314c38fdf9a7262dc95229d2370f3ae7a3bda7d6cf264f0c25(
    *,
    build_and_test: typing.Optional[typing.Sequence[builtins.str]] = None,
    deploy_environment: typing.Optional[typing.Sequence[builtins.str]] = None,
    destroy_environment: typing.Optional[typing.Sequence[builtins.str]] = None,
    install: typing.Optional[typing.Sequence[builtins.str]] = None,
    post_deploy_environment: typing.Optional[typing.Sequence[builtins.str]] = None,
    post_destroy_environment: typing.Optional[typing.Sequence[builtins.str]] = None,
    pre_deploy_environment: typing.Optional[typing.Sequence[builtins.str]] = None,
    pre_destroy_environment: typing.Optional[typing.Sequence[builtins.str]] = None,
    pre_install: typing.Optional[typing.Sequence[builtins.str]] = None,
    synth_pipeline: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be38be79ae4e169cdad1ff5fa548afd5af816580eaf5ec1eca5799f6bf3ace32(
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    auto_synth: typing.Optional[builtins.bool] = None,
    context: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    default_stack_synthesizer: typing.Optional[_aws_cdk_ceddda9d.IReusableStackSynthesizer] = None,
    outdir: typing.Optional[builtins.str] = None,
    policy_validation_beta1: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPolicyValidationPluginBeta1]] = None,
    post_cli_context: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    stack_traces: typing.Optional[builtins.bool] = None,
    tree_metadata: typing.Optional[builtins.bool] = None,
    pipeline: typing.Sequence[typing.Union[typing.Union[WaveDeployment, typing.Dict[builtins.str, typing.Any]], typing.Union[EnvironmentDeployment, typing.Dict[builtins.str, typing.Any]]]],
    repository: typing.Union[RepositoryProps, typing.Dict[builtins.str, typing.Any]],
    stacks: IStacksCreation,
    cdk_output_directory: typing.Optional[builtins.str] = None,
    code_build: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    code_pipeline: typing.Optional[typing.Union[CodePipelineOverrides, typing.Dict[builtins.str, typing.Any]]] = None,
    commands: typing.Optional[typing.Union[BuildCommands, typing.Dict[builtins.str, typing.Any]]] = None,
    fix_paths_metadata: typing.Optional[builtins.bool] = None,
    package_manager: typing.Optional[builtins.str] = None,
    prefix_stack_id_with_project_name: typing.Optional[builtins.bool] = None,
    slack_notifications: typing.Optional[typing.Union[SlackNotifications, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7bac62224aec74b6d37f678f5bdede0184616abc1fb2eafb3a4aa19f1c20fd4(
    *,
    asset_publishing_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    docker_credentials: typing.Optional[typing.Sequence[_aws_cdk_pipelines_ceddda9d.DockerCredential]] = None,
    docker_enabled_for_self_mutation: typing.Optional[builtins.bool] = None,
    docker_enabled_for_synth: typing.Optional[builtins.bool] = None,
    enable_key_rotation: typing.Optional[builtins.bool] = None,
    pipeline_name: typing.Optional[builtins.str] = None,
    publish_assets_in_parallel: typing.Optional[builtins.bool] = None,
    reuse_cross_region_support_stacks: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    self_mutation: typing.Optional[builtins.bool] = None,
    self_mutation_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    synth_code_build_defaults: typing.Optional[typing.Union[_aws_cdk_pipelines_ceddda9d.CodeBuildOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    use_change_sets: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a56d8f8652385a6beef9373eed0946aec4a1e2ca901b17252542af97a91c99a(
    *,
    environment: builtins.str,
    manual_approval: typing.Optional[builtins.bool] = None,
    post: typing.Optional[typing.Sequence[builtins.str]] = None,
    pre: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f94daa933ae3ad6d5e4b09fd8274268c1c6c4ce67db84eea5360a505e3c5d56(
    scope: _constructs_77d1e7e8.Construct,
    project_name: builtins.str,
    env_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6f830ab1d423354edc601071d8aae1b0849f4eb33644f06838e41508d8ba714(
    *,
    host: builtins.str,
    name: builtins.str,
    default_branch: typing.Optional[builtins.str] = None,
    feature_branch_prefixes: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6dccc8f244e67e4c56e0d08fc41124131552dcc2c40cdde13de9d458d473882(
    *,
    channel_id: builtins.str,
    workspace_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62e47fdb1eef2b0738fcc2152a329dd258aee175431814841e5687481f56c87b(
    *,
    feature_branch_failures: typing.Optional[typing.Union[SlackChannelConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    main_pipeline_failures: typing.Optional[typing.Union[SlackChannelConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e2f9daf95ae58e92db6a6c5f2f46d1d02b4f767b770eaf9116fc04ca2c5158e(
    *,
    environments: typing.Sequence[typing.Union[EnvironmentDeployment, typing.Dict[builtins.str, typing.Any]]],
    wave: builtins.str,
    manual_approval: typing.Optional[builtins.bool] = None,
    post: typing.Optional[typing.Sequence[builtins.str]] = None,
    post_each_environment: typing.Optional[typing.Sequence[builtins.str]] = None,
    pre: typing.Optional[typing.Sequence[builtins.str]] = None,
    pre_each_environment: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
