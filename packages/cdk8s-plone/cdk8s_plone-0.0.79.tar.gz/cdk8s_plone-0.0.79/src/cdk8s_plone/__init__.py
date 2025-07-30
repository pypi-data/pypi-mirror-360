r'''
# CMS Plone Chart for CDK8S

This chart provides a library to bootstrap a Plone deployment on a Kubernetes cluster using the [CDK8S](https://cdk8s.io) framework.

It provides

* Backend (as API with `plone.volto` or as Classic-UI)
* Frontend (Plone-Volto, a ReactJS based user interface)
* Varnish using kube-httpcache. It includes a way to invalidate varnish cluster (optional)

### Typescript

To use this library, create a new CDK8S project (or use an existing one)

```bash
cdk8s init typescript-app
```

Then add the following dependency to `package.json`:

```json
{
  "dependencies": {
    "@bluedynamics/cdk8s-plone": "*"
  }
}
```

Run `npm install` to install [cdk8s-plone](https://www.npmjs.com/package/@bluedynamics/cdk8s-plone).

### Python

Todo: Document in details how to install.

```bash
cdk8s init python-app
```

Python package name is [cdk8s-plone](https://pypi.org/project/cdk8s-plone/).

## Usage

With `cdk8s-cli` installed, create a new project:

```bash
cdk8s sythn
```

Add the following code to your `main.ts`:

```python
...
import { Plone } from '@bluedynamics/cdk8s-plone';
...
    super(scope, id, props);

    // define resources here
    new Plone(this, 'Plone', {});
...
```

Run `npm run build ` to generate the Kubernetes manifests.
The manifests are stored in the `dist` directory.

For more have a look at the [example project](https://github.com/bluedynamics/cdk8s-plone-example).

### Prerequisites

For using cdk8s-plone, we assume you already have following tools installed:

* kubectl – A command-line tool for interacting with Kubernetes clusters. For deploying the Kubernetes manifest you will need a tool like this. Take a look at the [Install Tools](https://kubernetes.io/docs/tasks/tools/#kubectl) for kubectl.
* (optional) Helm – A Kubernetes package manager for managing Plone/Volto deployments. This tool is optional and only needed if you generate helm charts as output with cdk8s synth - instead of pure manifests. There are several ways to install it see the [install section](https://helm.sh/docs/intro/install/) for Helm.

### References

[Kubernetes Documentation](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/) relevant for ressource management, readiness and liveness

#### PloneBaseOptions

*Interface*

* `image`(string):

  * The used Plone image
  * e.g. `plone/plone-backend:6.1.0`
* `imagePullPolicy`(string):

  * default `IfNotPresent`
* `replicas`(numbers)
* `maxUnavailable`(number|string)
* `minAvailable`(number|string)
* `limitCpu`(string)
* `limitMemory`(string)
* `requestCpu`(string)
* `requestMemory`(string)
* `environment`(kplus.Env)
* `readinessEnabled`(boolean)
* `readinessInitialDelaySeconds`(number)
* `readinessIimeoutSeconds`(number)
* `readinessPeriodSeconds`(number)
* `readinessSuccessThreshold`(number)
* `readinessFailureThreshold`(number)
* `livenessEnabled`(boolean)

  * should be `true` for `volto`
  * should be `false` for `backend/classicui`
* `livenessInitialDelaySeconds`(number)
* `livenessIimeoutSeconds`(number)
* `livenessPeriodSeconds`(number)
* `livenessSuccessThreshold`(number)
* `livenessFailureThreshold`(number)

#### PloneOptions

*Interface*

* `version`(string):

  * version of your project
* `siteId`(string):

  * default `Plone`
* `variant`(PloneVariant):

  * default `PloneVariant.VOLTO`
* `backend` (PloneBaseOptions):

  * default `{}`
  * needs `image` and `enviroment`
* `frontend` (PloneBaseOptions):

  * default `{}`
  * needs `image` if `PloneVariant.VOLTO`
* `imagePullSecrets`(string[])

#### PloneVariants

*Enum*

* VOLTO = 'volto'
* CLASSICUI  = 'classicui'

  * no frontend options/image needed

#### Plone

*class*

builds the `Plone` Construct

* `backendServiceName`(string)
* `frontendServiceName`(string)
* `variant`(PloneVariant)

  * default `Volto`
* `siteId`(string)

  * default `Plone`

#### PloneHttpcacheOptions

*Interface*

* `plone`(Plone):

  * Plone chart
* `varnishVcl`{string}:

  * varnishfile
  * per default `varnishVclFile` should be used
* `varnishVclFile`(string):

  * File in config folder
* `existingSecret`(string)
* `limitCpu`(string)
* `limitMemory`(string)
* `requestCpu`(string)
* `requestMemory`(string)
* `servicemonitor`(string)

  * default `false` used for metrics

#### PloneHttpcache

*class*

uses helmchart [kube-httpcache](https://github.com/mittwald/kube-httpcache) and builds the `PloneHttpCache` Construct

* `scope`(Construct)
* `id`(string)
* `options`(PloneHttpcacheOptions)

## Development

Clone the repository and install the dependencies:

```bash
nvm use lts/*
corepack enable
npx projen
```

Then run the following command to run the test:

```bash
npx projen test
```

## ToDo

* [ ] Option to enable Servicemonitor
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

import cdk8s_plus_30 as _cdk8s_plus_30_fa3b8a6f
import constructs as _constructs_77d1e7e8


class Plone(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@bluedynamics/cdk8s-plone.Plone",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        backend: typing.Optional[typing.Union["PloneBaseOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        frontend: typing.Optional[typing.Union["PloneBaseOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        image_pull_secrets: typing.Optional[typing.Sequence[builtins.str]] = None,
        site_id: typing.Optional[builtins.str] = None,
        variant: typing.Optional["PloneVariant"] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param backend: 
        :param frontend: 
        :param image_pull_secrets: 
        :param site_id: 
        :param variant: 
        :param version: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__543cbcb1139deb4ce75315c33bb5ebd6fd98851d9416a0f8e2c5cd960899e686)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = PloneOptions(
            backend=backend,
            frontend=frontend,
            image_pull_secrets=image_pull_secrets,
            site_id=site_id,
            variant=variant,
            version=version,
        )

        jsii.create(self.__class__, self, [scope, id, options])

    @builtins.property
    @jsii.member(jsii_name="backendServiceName")
    def backend_service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backendServiceName"))

    @builtins.property
    @jsii.member(jsii_name="siteId")
    def site_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "siteId"))

    @builtins.property
    @jsii.member(jsii_name="variant")
    def variant(self) -> "PloneVariant":
        return typing.cast("PloneVariant", jsii.get(self, "variant"))

    @builtins.property
    @jsii.member(jsii_name="frontendServiceName")
    def frontend_service_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "frontendServiceName"))


@jsii.data_type(
    jsii_type="@bluedynamics/cdk8s-plone.PloneBaseOptions",
    jsii_struct_bases=[],
    name_mapping={
        "environment": "environment",
        "image": "image",
        "image_pull_policy": "imagePullPolicy",
        "limit_cpu": "limitCpu",
        "limit_memory": "limitMemory",
        "liveness_enabled": "livenessEnabled",
        "liveness_failure_threshold": "livenessFailureThreshold",
        "liveness_iimeout_seconds": "livenessIimeoutSeconds",
        "liveness_initial_delay_seconds": "livenessInitialDelaySeconds",
        "liveness_period_seconds": "livenessPeriodSeconds",
        "liveness_success_threshold": "livenessSuccessThreshold",
        "max_unavailable": "maxUnavailable",
        "min_available": "minAvailable",
        "readiness_enabled": "readinessEnabled",
        "readiness_failure_threshold": "readinessFailureThreshold",
        "readiness_iimeout_seconds": "readinessIimeoutSeconds",
        "readiness_initial_delay_seconds": "readinessInitialDelaySeconds",
        "readiness_period_seconds": "readinessPeriodSeconds",
        "readiness_success_threshold": "readinessSuccessThreshold",
        "replicas": "replicas",
        "request_cpu": "requestCpu",
        "request_memory": "requestMemory",
    },
)
class PloneBaseOptions:
    def __init__(
        self,
        *,
        environment: typing.Optional[_cdk8s_plus_30_fa3b8a6f.Env] = None,
        image: typing.Optional[builtins.str] = None,
        image_pull_policy: typing.Optional[builtins.str] = None,
        limit_cpu: typing.Optional[builtins.str] = None,
        limit_memory: typing.Optional[builtins.str] = None,
        liveness_enabled: typing.Optional[builtins.bool] = None,
        liveness_failure_threshold: typing.Optional[jsii.Number] = None,
        liveness_iimeout_seconds: typing.Optional[jsii.Number] = None,
        liveness_initial_delay_seconds: typing.Optional[jsii.Number] = None,
        liveness_period_seconds: typing.Optional[jsii.Number] = None,
        liveness_success_threshold: typing.Optional[jsii.Number] = None,
        max_unavailable: typing.Optional[typing.Union[builtins.str, jsii.Number]] = None,
        min_available: typing.Optional[typing.Union[builtins.str, jsii.Number]] = None,
        readiness_enabled: typing.Optional[builtins.bool] = None,
        readiness_failure_threshold: typing.Optional[jsii.Number] = None,
        readiness_iimeout_seconds: typing.Optional[jsii.Number] = None,
        readiness_initial_delay_seconds: typing.Optional[jsii.Number] = None,
        readiness_period_seconds: typing.Optional[jsii.Number] = None,
        readiness_success_threshold: typing.Optional[jsii.Number] = None,
        replicas: typing.Optional[jsii.Number] = None,
        request_cpu: typing.Optional[builtins.str] = None,
        request_memory: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param environment: 
        :param image: 
        :param image_pull_policy: 
        :param limit_cpu: 
        :param limit_memory: 
        :param liveness_enabled: 
        :param liveness_failure_threshold: 
        :param liveness_iimeout_seconds: 
        :param liveness_initial_delay_seconds: 
        :param liveness_period_seconds: 
        :param liveness_success_threshold: 
        :param max_unavailable: 
        :param min_available: 
        :param readiness_enabled: 
        :param readiness_failure_threshold: 
        :param readiness_iimeout_seconds: 
        :param readiness_initial_delay_seconds: 
        :param readiness_period_seconds: 
        :param readiness_success_threshold: 
        :param replicas: 
        :param request_cpu: 
        :param request_memory: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd9cf17a63ac3f69f433db3caa859d98a750929386f09ada26dd0fd212b3ec78)
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument image", value=image, expected_type=type_hints["image"])
            check_type(argname="argument image_pull_policy", value=image_pull_policy, expected_type=type_hints["image_pull_policy"])
            check_type(argname="argument limit_cpu", value=limit_cpu, expected_type=type_hints["limit_cpu"])
            check_type(argname="argument limit_memory", value=limit_memory, expected_type=type_hints["limit_memory"])
            check_type(argname="argument liveness_enabled", value=liveness_enabled, expected_type=type_hints["liveness_enabled"])
            check_type(argname="argument liveness_failure_threshold", value=liveness_failure_threshold, expected_type=type_hints["liveness_failure_threshold"])
            check_type(argname="argument liveness_iimeout_seconds", value=liveness_iimeout_seconds, expected_type=type_hints["liveness_iimeout_seconds"])
            check_type(argname="argument liveness_initial_delay_seconds", value=liveness_initial_delay_seconds, expected_type=type_hints["liveness_initial_delay_seconds"])
            check_type(argname="argument liveness_period_seconds", value=liveness_period_seconds, expected_type=type_hints["liveness_period_seconds"])
            check_type(argname="argument liveness_success_threshold", value=liveness_success_threshold, expected_type=type_hints["liveness_success_threshold"])
            check_type(argname="argument max_unavailable", value=max_unavailable, expected_type=type_hints["max_unavailable"])
            check_type(argname="argument min_available", value=min_available, expected_type=type_hints["min_available"])
            check_type(argname="argument readiness_enabled", value=readiness_enabled, expected_type=type_hints["readiness_enabled"])
            check_type(argname="argument readiness_failure_threshold", value=readiness_failure_threshold, expected_type=type_hints["readiness_failure_threshold"])
            check_type(argname="argument readiness_iimeout_seconds", value=readiness_iimeout_seconds, expected_type=type_hints["readiness_iimeout_seconds"])
            check_type(argname="argument readiness_initial_delay_seconds", value=readiness_initial_delay_seconds, expected_type=type_hints["readiness_initial_delay_seconds"])
            check_type(argname="argument readiness_period_seconds", value=readiness_period_seconds, expected_type=type_hints["readiness_period_seconds"])
            check_type(argname="argument readiness_success_threshold", value=readiness_success_threshold, expected_type=type_hints["readiness_success_threshold"])
            check_type(argname="argument replicas", value=replicas, expected_type=type_hints["replicas"])
            check_type(argname="argument request_cpu", value=request_cpu, expected_type=type_hints["request_cpu"])
            check_type(argname="argument request_memory", value=request_memory, expected_type=type_hints["request_memory"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if environment is not None:
            self._values["environment"] = environment
        if image is not None:
            self._values["image"] = image
        if image_pull_policy is not None:
            self._values["image_pull_policy"] = image_pull_policy
        if limit_cpu is not None:
            self._values["limit_cpu"] = limit_cpu
        if limit_memory is not None:
            self._values["limit_memory"] = limit_memory
        if liveness_enabled is not None:
            self._values["liveness_enabled"] = liveness_enabled
        if liveness_failure_threshold is not None:
            self._values["liveness_failure_threshold"] = liveness_failure_threshold
        if liveness_iimeout_seconds is not None:
            self._values["liveness_iimeout_seconds"] = liveness_iimeout_seconds
        if liveness_initial_delay_seconds is not None:
            self._values["liveness_initial_delay_seconds"] = liveness_initial_delay_seconds
        if liveness_period_seconds is not None:
            self._values["liveness_period_seconds"] = liveness_period_seconds
        if liveness_success_threshold is not None:
            self._values["liveness_success_threshold"] = liveness_success_threshold
        if max_unavailable is not None:
            self._values["max_unavailable"] = max_unavailable
        if min_available is not None:
            self._values["min_available"] = min_available
        if readiness_enabled is not None:
            self._values["readiness_enabled"] = readiness_enabled
        if readiness_failure_threshold is not None:
            self._values["readiness_failure_threshold"] = readiness_failure_threshold
        if readiness_iimeout_seconds is not None:
            self._values["readiness_iimeout_seconds"] = readiness_iimeout_seconds
        if readiness_initial_delay_seconds is not None:
            self._values["readiness_initial_delay_seconds"] = readiness_initial_delay_seconds
        if readiness_period_seconds is not None:
            self._values["readiness_period_seconds"] = readiness_period_seconds
        if readiness_success_threshold is not None:
            self._values["readiness_success_threshold"] = readiness_success_threshold
        if replicas is not None:
            self._values["replicas"] = replicas
        if request_cpu is not None:
            self._values["request_cpu"] = request_cpu
        if request_memory is not None:
            self._values["request_memory"] = request_memory

    @builtins.property
    def environment(self) -> typing.Optional[_cdk8s_plus_30_fa3b8a6f.Env]:
        result = self._values.get("environment")
        return typing.cast(typing.Optional[_cdk8s_plus_30_fa3b8a6f.Env], result)

    @builtins.property
    def image(self) -> typing.Optional[builtins.str]:
        result = self._values.get("image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_pull_policy(self) -> typing.Optional[builtins.str]:
        result = self._values.get("image_pull_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def limit_cpu(self) -> typing.Optional[builtins.str]:
        result = self._values.get("limit_cpu")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def limit_memory(self) -> typing.Optional[builtins.str]:
        result = self._values.get("limit_memory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def liveness_enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("liveness_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def liveness_failure_threshold(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("liveness_failure_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def liveness_iimeout_seconds(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("liveness_iimeout_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def liveness_initial_delay_seconds(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("liveness_initial_delay_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def liveness_period_seconds(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("liveness_period_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def liveness_success_threshold(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("liveness_success_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_unavailable(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, jsii.Number]]:
        result = self._values.get("max_unavailable")
        return typing.cast(typing.Optional[typing.Union[builtins.str, jsii.Number]], result)

    @builtins.property
    def min_available(self) -> typing.Optional[typing.Union[builtins.str, jsii.Number]]:
        result = self._values.get("min_available")
        return typing.cast(typing.Optional[typing.Union[builtins.str, jsii.Number]], result)

    @builtins.property
    def readiness_enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("readiness_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def readiness_failure_threshold(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("readiness_failure_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def readiness_iimeout_seconds(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("readiness_iimeout_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def readiness_initial_delay_seconds(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("readiness_initial_delay_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def readiness_period_seconds(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("readiness_period_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def readiness_success_threshold(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("readiness_success_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def replicas(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def request_cpu(self) -> typing.Optional[builtins.str]:
        result = self._values.get("request_cpu")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_memory(self) -> typing.Optional[builtins.str]:
        result = self._values.get("request_memory")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PloneBaseOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PloneHttpcache(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@bluedynamics/cdk8s-plone.PloneHttpcache",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        plone: Plone,
        existing_secret: typing.Optional[builtins.str] = None,
        limit_cpu: typing.Optional[builtins.str] = None,
        limit_memory: typing.Optional[builtins.str] = None,
        request_cpu: typing.Optional[builtins.str] = None,
        request_memory: typing.Optional[builtins.str] = None,
        servicemonitor: typing.Optional[builtins.bool] = None,
        varnish_vcl: typing.Optional[builtins.str] = None,
        varnish_vcl_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param plone: plone chart. Default: - none
        :param existing_secret: existingSecret - Read admin credentials from user provided secret. Default: - undefined
        :param limit_cpu: 
        :param limit_memory: 
        :param request_cpu: 
        :param request_memory: 
        :param servicemonitor: 
        :param varnish_vcl: varnishVcl. Default: - file in config folder
        :param varnish_vcl_file: varnishVclFile. Default: - undefined
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7f85fe682616b18a7851bccc28d7021f541060ebc9eba02965066fd28589e69)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = PloneHttpcacheOptions(
            plone=plone,
            existing_secret=existing_secret,
            limit_cpu=limit_cpu,
            limit_memory=limit_memory,
            request_cpu=request_cpu,
            request_memory=request_memory,
            servicemonitor=servicemonitor,
            varnish_vcl=varnish_vcl,
            varnish_vcl_file=varnish_vcl_file,
        )

        jsii.create(self.__class__, self, [scope, id, options])

    @builtins.property
    @jsii.member(jsii_name="httpcacheServiceName")
    def httpcache_service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpcacheServiceName"))


@jsii.data_type(
    jsii_type="@bluedynamics/cdk8s-plone.PloneHttpcacheOptions",
    jsii_struct_bases=[],
    name_mapping={
        "plone": "plone",
        "existing_secret": "existingSecret",
        "limit_cpu": "limitCpu",
        "limit_memory": "limitMemory",
        "request_cpu": "requestCpu",
        "request_memory": "requestMemory",
        "servicemonitor": "servicemonitor",
        "varnish_vcl": "varnishVcl",
        "varnish_vcl_file": "varnishVclFile",
    },
)
class PloneHttpcacheOptions:
    def __init__(
        self,
        *,
        plone: Plone,
        existing_secret: typing.Optional[builtins.str] = None,
        limit_cpu: typing.Optional[builtins.str] = None,
        limit_memory: typing.Optional[builtins.str] = None,
        request_cpu: typing.Optional[builtins.str] = None,
        request_memory: typing.Optional[builtins.str] = None,
        servicemonitor: typing.Optional[builtins.bool] = None,
        varnish_vcl: typing.Optional[builtins.str] = None,
        varnish_vcl_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param plone: plone chart. Default: - none
        :param existing_secret: existingSecret - Read admin credentials from user provided secret. Default: - undefined
        :param limit_cpu: 
        :param limit_memory: 
        :param request_cpu: 
        :param request_memory: 
        :param servicemonitor: 
        :param varnish_vcl: varnishVcl. Default: - file in config folder
        :param varnish_vcl_file: varnishVclFile. Default: - undefined
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f974bf721e34d8993ba90020605bc5e09424793236af8b8c5a9bb9a63f1974a)
            check_type(argname="argument plone", value=plone, expected_type=type_hints["plone"])
            check_type(argname="argument existing_secret", value=existing_secret, expected_type=type_hints["existing_secret"])
            check_type(argname="argument limit_cpu", value=limit_cpu, expected_type=type_hints["limit_cpu"])
            check_type(argname="argument limit_memory", value=limit_memory, expected_type=type_hints["limit_memory"])
            check_type(argname="argument request_cpu", value=request_cpu, expected_type=type_hints["request_cpu"])
            check_type(argname="argument request_memory", value=request_memory, expected_type=type_hints["request_memory"])
            check_type(argname="argument servicemonitor", value=servicemonitor, expected_type=type_hints["servicemonitor"])
            check_type(argname="argument varnish_vcl", value=varnish_vcl, expected_type=type_hints["varnish_vcl"])
            check_type(argname="argument varnish_vcl_file", value=varnish_vcl_file, expected_type=type_hints["varnish_vcl_file"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "plone": plone,
        }
        if existing_secret is not None:
            self._values["existing_secret"] = existing_secret
        if limit_cpu is not None:
            self._values["limit_cpu"] = limit_cpu
        if limit_memory is not None:
            self._values["limit_memory"] = limit_memory
        if request_cpu is not None:
            self._values["request_cpu"] = request_cpu
        if request_memory is not None:
            self._values["request_memory"] = request_memory
        if servicemonitor is not None:
            self._values["servicemonitor"] = servicemonitor
        if varnish_vcl is not None:
            self._values["varnish_vcl"] = varnish_vcl
        if varnish_vcl_file is not None:
            self._values["varnish_vcl_file"] = varnish_vcl_file

    @builtins.property
    def plone(self) -> Plone:
        '''plone chart.

        :default: - none
        '''
        result = self._values.get("plone")
        assert result is not None, "Required property 'plone' is missing"
        return typing.cast(Plone, result)

    @builtins.property
    def existing_secret(self) -> typing.Optional[builtins.str]:
        '''existingSecret - Read admin credentials from user provided secret.

        :default: - undefined
        '''
        result = self._values.get("existing_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def limit_cpu(self) -> typing.Optional[builtins.str]:
        result = self._values.get("limit_cpu")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def limit_memory(self) -> typing.Optional[builtins.str]:
        result = self._values.get("limit_memory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_cpu(self) -> typing.Optional[builtins.str]:
        result = self._values.get("request_cpu")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_memory(self) -> typing.Optional[builtins.str]:
        result = self._values.get("request_memory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def servicemonitor(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("servicemonitor")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def varnish_vcl(self) -> typing.Optional[builtins.str]:
        '''varnishVcl.

        :default: - file in config folder
        '''
        result = self._values.get("varnish_vcl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def varnish_vcl_file(self) -> typing.Optional[builtins.str]:
        '''varnishVclFile.

        :default: - undefined
        '''
        result = self._values.get("varnish_vcl_file")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PloneHttpcacheOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@bluedynamics/cdk8s-plone.PloneOptions",
    jsii_struct_bases=[],
    name_mapping={
        "backend": "backend",
        "frontend": "frontend",
        "image_pull_secrets": "imagePullSecrets",
        "site_id": "siteId",
        "variant": "variant",
        "version": "version",
    },
)
class PloneOptions:
    def __init__(
        self,
        *,
        backend: typing.Optional[typing.Union[PloneBaseOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        frontend: typing.Optional[typing.Union[PloneBaseOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        image_pull_secrets: typing.Optional[typing.Sequence[builtins.str]] = None,
        site_id: typing.Optional[builtins.str] = None,
        variant: typing.Optional["PloneVariant"] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param backend: 
        :param frontend: 
        :param image_pull_secrets: 
        :param site_id: 
        :param variant: 
        :param version: 
        '''
        if isinstance(backend, dict):
            backend = PloneBaseOptions(**backend)
        if isinstance(frontend, dict):
            frontend = PloneBaseOptions(**frontend)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d92a415ce6a72ab45cd3d3e169acc7fc8156c275bc6268fa1eed4110e990c22a)
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument frontend", value=frontend, expected_type=type_hints["frontend"])
            check_type(argname="argument image_pull_secrets", value=image_pull_secrets, expected_type=type_hints["image_pull_secrets"])
            check_type(argname="argument site_id", value=site_id, expected_type=type_hints["site_id"])
            check_type(argname="argument variant", value=variant, expected_type=type_hints["variant"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if backend is not None:
            self._values["backend"] = backend
        if frontend is not None:
            self._values["frontend"] = frontend
        if image_pull_secrets is not None:
            self._values["image_pull_secrets"] = image_pull_secrets
        if site_id is not None:
            self._values["site_id"] = site_id
        if variant is not None:
            self._values["variant"] = variant
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def backend(self) -> typing.Optional[PloneBaseOptions]:
        result = self._values.get("backend")
        return typing.cast(typing.Optional[PloneBaseOptions], result)

    @builtins.property
    def frontend(self) -> typing.Optional[PloneBaseOptions]:
        result = self._values.get("frontend")
        return typing.cast(typing.Optional[PloneBaseOptions], result)

    @builtins.property
    def image_pull_secrets(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("image_pull_secrets")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def site_id(self) -> typing.Optional[builtins.str]:
        result = self._values.get("site_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def variant(self) -> typing.Optional["PloneVariant"]:
        result = self._values.get("variant")
        return typing.cast(typing.Optional["PloneVariant"], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PloneOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@bluedynamics/cdk8s-plone.PloneVariant")
class PloneVariant(enum.Enum):
    VOLTO = "VOLTO"
    CLASSICUI = "CLASSICUI"


__all__ = [
    "Plone",
    "PloneBaseOptions",
    "PloneHttpcache",
    "PloneHttpcacheOptions",
    "PloneOptions",
    "PloneVariant",
]

publication.publish()

def _typecheckingstub__543cbcb1139deb4ce75315c33bb5ebd6fd98851d9416a0f8e2c5cd960899e686(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    backend: typing.Optional[typing.Union[PloneBaseOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    frontend: typing.Optional[typing.Union[PloneBaseOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    image_pull_secrets: typing.Optional[typing.Sequence[builtins.str]] = None,
    site_id: typing.Optional[builtins.str] = None,
    variant: typing.Optional[PloneVariant] = None,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd9cf17a63ac3f69f433db3caa859d98a750929386f09ada26dd0fd212b3ec78(
    *,
    environment: typing.Optional[_cdk8s_plus_30_fa3b8a6f.Env] = None,
    image: typing.Optional[builtins.str] = None,
    image_pull_policy: typing.Optional[builtins.str] = None,
    limit_cpu: typing.Optional[builtins.str] = None,
    limit_memory: typing.Optional[builtins.str] = None,
    liveness_enabled: typing.Optional[builtins.bool] = None,
    liveness_failure_threshold: typing.Optional[jsii.Number] = None,
    liveness_iimeout_seconds: typing.Optional[jsii.Number] = None,
    liveness_initial_delay_seconds: typing.Optional[jsii.Number] = None,
    liveness_period_seconds: typing.Optional[jsii.Number] = None,
    liveness_success_threshold: typing.Optional[jsii.Number] = None,
    max_unavailable: typing.Optional[typing.Union[builtins.str, jsii.Number]] = None,
    min_available: typing.Optional[typing.Union[builtins.str, jsii.Number]] = None,
    readiness_enabled: typing.Optional[builtins.bool] = None,
    readiness_failure_threshold: typing.Optional[jsii.Number] = None,
    readiness_iimeout_seconds: typing.Optional[jsii.Number] = None,
    readiness_initial_delay_seconds: typing.Optional[jsii.Number] = None,
    readiness_period_seconds: typing.Optional[jsii.Number] = None,
    readiness_success_threshold: typing.Optional[jsii.Number] = None,
    replicas: typing.Optional[jsii.Number] = None,
    request_cpu: typing.Optional[builtins.str] = None,
    request_memory: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7f85fe682616b18a7851bccc28d7021f541060ebc9eba02965066fd28589e69(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    plone: Plone,
    existing_secret: typing.Optional[builtins.str] = None,
    limit_cpu: typing.Optional[builtins.str] = None,
    limit_memory: typing.Optional[builtins.str] = None,
    request_cpu: typing.Optional[builtins.str] = None,
    request_memory: typing.Optional[builtins.str] = None,
    servicemonitor: typing.Optional[builtins.bool] = None,
    varnish_vcl: typing.Optional[builtins.str] = None,
    varnish_vcl_file: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f974bf721e34d8993ba90020605bc5e09424793236af8b8c5a9bb9a63f1974a(
    *,
    plone: Plone,
    existing_secret: typing.Optional[builtins.str] = None,
    limit_cpu: typing.Optional[builtins.str] = None,
    limit_memory: typing.Optional[builtins.str] = None,
    request_cpu: typing.Optional[builtins.str] = None,
    request_memory: typing.Optional[builtins.str] = None,
    servicemonitor: typing.Optional[builtins.bool] = None,
    varnish_vcl: typing.Optional[builtins.str] = None,
    varnish_vcl_file: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d92a415ce6a72ab45cd3d3e169acc7fc8156c275bc6268fa1eed4110e990c22a(
    *,
    backend: typing.Optional[typing.Union[PloneBaseOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    frontend: typing.Optional[typing.Union[PloneBaseOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    image_pull_secrets: typing.Optional[typing.Sequence[builtins.str]] = None,
    site_id: typing.Optional[builtins.str] = None,
    variant: typing.Optional[PloneVariant] = None,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
