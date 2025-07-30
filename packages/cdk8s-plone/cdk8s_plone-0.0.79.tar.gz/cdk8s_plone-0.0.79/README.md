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
