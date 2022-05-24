#!/usr/bin/env python

import os
import argparse
import urllib3
import kubetools
import controller

def parseArgs():
    parser = argparse.ArgumentParser(description='Horizon kubernetes flow autoscaler')
    parser.add_argument('--verbose', '-v', action='count', help='Verbosity level')
    parser.add_argument('--noAction', action='store_true', help='Do not modify anything')
    parser.add_argument('--defsYaml', default='defs.yaml', help='Defs file')
    parser.add_argument('--minActionAge', '-m', type=int, default=120, help='Minimum time between scaling actions on a single resource')
    return parser.parse_args()

def main():
    urllib3.disable_warnings() # Temporary workaround
    args = parseArgs()
    kubetools.logLevel = args.verbose
    kubetools.loadKubernetesConfig()
    mainController = controller.Controller(args)
    mainController.scalerLoop()

if __name__ == '__main__':
    main()
