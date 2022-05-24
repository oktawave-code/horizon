## Flowcontroller

It’s a custom Kubernetes controller created by Oktawave. It allows you to create an abstract representation of complete systems using the basic resources provided by k8s.

### What’s the problem?

The basic K8S resources (e.g. Deployment, StatefulSet) focus on managing one application in one definition. Modern systems consist of many different applications, thus requiring the cluster operator to define a set of definitions for each application. If you need to run multiple instances of such a system in parallel in one cluster, there is a problem of gigantic configuration increase and the problem of their management by administrators and developers. This is really hard to maintain and automate.
Flowcontroller solves this problem by being able to build one resource representing the entire system and all its definitions. This new type is a form of Kubernetes extension, manageable and fully integrated with its API.

### Components

* Controller - the main management module
* System definitions - a set of resource definitions that make up the system (Deployments, Configmaps, Services, etc ...)
* CRD - Custom resource definition, a resource that extends the basic K8S API with a new resource type that represents the entire system

### How does it work?

Flowcontroller monitors the established objects defined by CRD and on this basis performs the action of creating, updating or removing resources from the cluster. These resources are provided in the form of YAML files with definitions of individual component applications.
When a new resource represented by CRD is created, all YAMLs are automatically applied to the cluster.
Flowcontroller also provides a simple definition parameterization system - system definitions can have special tags with references representing paths in CRD observed by flowcontroller. Each field is filled with the desired values ​​before applying the definition to the cluster.

### Unsolved issues

* This tool was written for python 2.7 which is obsolete by now
* Some features are missing - they were not needed for our use case, so we left them "for later"
* Code is poorly commented (nice docstrings will be made hopefully)
* Some k8s interactions are not very elegant (when this code was created, k8s python libraries were pretty slim, so we did lots of guessing)