Streaming Worker
========================================================================================================================================
The role of the Streaming Worker is to listen to a particular topic of the Kafka cluster and consume the incoming messages. Streaming data is divided into batches (according to a time interval). These batches are deserialized by the Worker, according to the supported Avro schema, parsed and registered in the corresponding table of Hive.<br />
Streaming Worker can only run on the central infrastructure and it can be deployed in local, client or cluster mode.

## Prerequisites
Dependencies in Python:
* [avro](https://avro.apache.org/) - Data serialization system.

## Installation
_-- will be updated soon --_

## Configuration
_-- will be updated soon --_

## Start Distributed Collector
_-- will be updated soon --_

### Print Usage Message
_-- will be updated soon --_

### Run
To start Streaming Worker:<br />
    ` spark2-submit --deploy-mode cluster --py-files /tmp/worker.zip,/tmp/avro.zip worker/streaming.py -d <database> -t <pipeline> -p <partition> --topic <topic> -z <zkquorum> 2>/dev/null`
