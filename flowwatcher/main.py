#!/usr/bin/env python

import os
import argparse
import urllib3
import kubetools
import controller

def parseArgs():
    parser = argparse.ArgumentParser(description='Horizon kubernetes flow tester')
    parser.add_argument('crdName', help='master CRD name')
    parser.add_argument('--verbose', '-v', action='count', help='Verbosity level')
    parser.add_argument('--noAction', action='store_true', help='Do not modify anything')
    parser.add_argument('--namespace', default='default', help='default namespace to use (if not supplied in masterYamls)')
    parser.add_argument('--namespacePath', default='/spec/namespace', help='path to namespace field in masterYamls')
    parser.add_argument('--tracebackLabel', default=None, help='name for traceback label used in every created resource')
    parser.add_argument('--excludedKinds', default='Event,MetricValueList,PodMetrics,PersistentVolumeClaim,ComponentStatus,Endpoints', help='kinds to exclude form test')
    return parser.parse_args()

def main():
    urllib3.disable_warnings() # Temporary workaround
    args = parseArgs()
    kubetools.logLevel = args.verbose
    kubetools.loadKubernetesConfig()
    mainController = controller.Controller(args)
    mainController.watcherLoop()

if __name__ == '__main__':
    main()
