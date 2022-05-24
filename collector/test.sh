#!/usr/bin/env bash

testpart () {
	RESP=`echo $1|xargs curl -s -X POST`
	ACK=`echo "$RESP"|head -1`
	if [ "x$ACK" != "xConsumed." ]
	then
		echo Failed: $1
		echo "$RESP"
	else
		TOPICS=`echo "$RESP"|awk '/^ => (.*)/{printf("%s,", $2)}'|tr -d '"'`
		if [ "x$TOPICS" != "x$2," ]
		then
			echo Failed: $1
			echo Expected: "$2"
			echo Got:
			echo "$RESP"
		else
			echo Ok: $1
		fi
	fi
}

TESTPORT=11112
TESTCONFIG=/tmp/testrouting.yaml

touch $TESTCONFIG

export LISTEN_PORT=$TESTPORT
export CLIENT_ID='user1'
export ROUTING='[{"filter":"/test","source":"url","topic":"test"},{"topic":"backup"},{"filter":"([a-z]+)","source":"X-Horizon-Routing","topic":"t-$1","final":true},{"filter":".+","source":"X-Topic","topic":"$0"}]'
export CONFIG_FILE=$TESTCONFIG
export VERBOSE=1

./collector &
SERVPID=$!

sleep 0.1
while [ 1 ]
do
	RESP=`curl -s -X GET 127.0.0.1:$TESTPORT/status`
	if [ "x$RESP" == "xOk." ]
	then
		break
	fi
	sleep 0.5
done

testpart "127.0.0.1:$TESTPORT/abc" "backup"
testpart "127.0.0.1:$TESTPORT/abc -H 'X-Horizon-Routing: abc'" "backup,t-abc"
testpart "127.0.0.1:$TESTPORT/test -H 'X-Horizon-Routing: abc'" "test,backup,t-abc"
testpart "127.0.0.1:$TESTPORT/xyz -H 'X-Horizon-Routing: 123' -H 'X-Topic: q'" "backup,q"
testpart "127.0.0.1:$TESTPORT/xyz -H 'X-Horizon-Routing: 123x' -H 'X-Topic: q'" "backup,t-x"
testpart "127.0.0.1:$TESTPORT/xyz -H 'X-Topic: q'" "backup,q"

cp test.yaml $TESTCONFIG
sleep 3

testpart "127.0.0.1:$TESTPORT/abc" "backup2"
testpart "127.0.0.1:$TESTPORT/abc -H 'X-Horizon-Routing: abc'" "backup2,x-abc"
testpart "127.0.0.1:$TESTPORT/xyz -H 'X-Horizon-Routing: 123' -H 'X-Topic: q'" "backup2"

kill $SERVPID

rm $TESTCONFIG
