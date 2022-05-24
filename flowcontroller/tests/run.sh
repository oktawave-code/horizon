#!/usr/bin/env bash

. .env/bin/activate

testpart () {
	R=`TEST=TESTVAR ./main.py --noAction -vvvv --crdName tests/crd.yaml --create tests/$1.yaml --yamlPath tests/$2|tail -1|tr -d " "`
	E=`echo $4|tr -d " "`
	if [ "$R" != "$E" ]
	then
		echo Test '"'$3'"' failed
		echo Expected: $E
		echo Got: $R
	else
		echo Test '"'$3'"' passed
	fi
}

testpart def1 yamlsOk1 numbers 'CallingCoreV1Api.create_namespaced_pod({"body": {"apiVersion": "v1", "kind": "pod", "metadata": {"annotations": {}, "name": "test-pod"}, "spec": {"resultIsNumber": {"conversionNotNeeded": 123, "explicitConversion": 123, "justUseProvidedType": 123}}}, "namespace": "default"})'
testpart def1 yamlsOk2 strings 'CallingCoreV1Api.create_namespaced_pod({"body": {"apiVersion": "v1", "kind": "pod", "metadata": {"annotations": {}, "name": "test-pod"}, "spec": {"resultIsString": {"concatenationForcesStringType": "123-someSuffix", "conversionNotNeeded": "blah", "evenForEdgeCases": "123", "explicitConversion": "123", "ignoredConversion": "somePrefix123", "justUseProvidedType": "blah", "serializedObject":"{\"a\":1,\"b\":\"abc\"}", "someOtherConcatenation": "blah123"}}}, "namespace": "default"})'
testpart def1 yamlsOk3 objects 'CallingCoreV1Api.create_namespaced_pod({"body": {"apiVersion": "v1", "kind": "pod", "metadata": {"annotations": {}, "name": "test-pod"}, "spec": {"resultIsObject": {"conversionNotNeeded": {"a": 1, "b": "abc"}, "includeEntireSubtree": {"a": 1, "b": "abc"}}}}, "namespace": "default"})'
testpart def1 yamlsOk4 env 'CallingCoreV1Api.create_namespaced_pod({"body": {"apiVersion": "v1", "kind": "pod", "metadata": {"annotations": {}, "name": "test-pod"}, "spec": {"includeEnv":"TESTVAR"}}, "namespace": "default"})'

testpart def1 yamlsErr1 missingVal 'Error: Missing value: missing'
testpart def1 yamlsErr2 strToInt 'Error: Not a number: str1:int'
testpart def1 yamlsErr3 objToInt 'Error: Not a number: obj:int'
testpart def1 yamlsErr4 objToStr 'Error: Can not convert to a string: obj'
testpart def1 yamlsErr5 strToObj 'Error: Not an object: str1:obj'
