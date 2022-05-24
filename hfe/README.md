## Build

```

# Builds HFE by using profile
mvn <goal> -P server

# Builds Flink executable JAR
mvn <goal> 

```

When run with environment variable "MODE" set to "SERVER", jar enters a server mode and listens on port 8000

There are two main REST endpoints:

* GET /defs
returns json with current graph component definitions

* POST /validator
validates graph passed in "json" post parameter
Response is either:

    http:200
    body:Okay

or

    http:400
    body:Error message

* There is also a GET /form endpoint, which returns simple html form for manual testing of /validator
