Distributed Collector
===============================================================================
The role of the Distributed Collector is similar, as it processes the data before transmission. Distributed Collector tracks a directory backwards for newly created files. When a file is detected, it converts it into CSV format and stores the output in the local staging area. Following to that, reads the CSV file line-by-line and creates smaller chunks of bytes. The size of each chunk depends on the maximum request size allowed by Kafka. Finally, it serializes each chunk into an Avro-encoded format and publishes them to Kafka cluster.<br />
Due to its architecture, Distributed Collector can run **on an edge node** of the Big Data infrastructure as well as **on a remote host** (proxy server, vNSF, etc).<br />
In addition, option `--skip-conversion` has been added. When this option is enabled, Distributed Collector expects already processed files in the CSV format. Hence, when it detects one, it does not apply any transformation; just splits it into chunks and transmits to the Kafka cluster.<br />
This option is also useful, when a segment failed to transmit to the Kafka cluster. By default, Distributed Collector stores the failed segment in CSV format under the local staging area. Then, using `--skip-conversion` option could be reloaded and sent to the Kafka cluster.<br />
Distributed Collector publishes to Apache Kafka only the CSV-converted file, and not the original one. The binary file remains to the local filesystem of the current host.

## Prerequisites
* [avro](https://avro.apache.org/) - Data serialization system.
* [kafka-python](https://github.com/dpkp/kafka-python) - Python client for the Apache Kafka distributed stream processing system.
* [watchdog](https://pypi.python.org/pypi/watchdog) - Python API and shell utilities to monitor file system events.

## Installation
Installation of Distributed Collector requires a user with `sudo` privileges. Enter `d-collector` directory and create the archive of the default format for the current platform:<br />
  `python setup.py sdist`

Then, install the source distribution you created:<br />
  `sudo -H pip install distributed-collector-0.9.1.beta.tar.gz`

If you want to avoid granting `sudo` permissions to the specific user (or keep isolated the current installation from the rest of the system), you can use the `virtualenv` package.
Install `virtualenv` package as `root` user<br />
  `sudo apt-get -y install python-virtualenv`

switch to your user and create an isolated virtual environment<br />
  `virtualenv --no-site-packages venv`

Finally, activate the virtual environment and install the Distributed Collector without `sudo` command:<br />
  `source venv/bin/activate`
  `python setup.py sdist`
  `pip install distributed-collector-0.9.1.beta.tar.gz`

## Configuration
Both Distributed Collector and Streaming Listener use the same configuration file as the original Spot Ingest flavour. The only addition is under `kafka` section:

    "kafka":{
        "kafka_server":"kafka ip",
        "kafka_port":"kafka port",
        "zookeper_server":"zk ip",
        "zookeper_port":"zk port",
        "message_size":900000,
        "max_request_size": 1048576
    },

The `max_request_size` defines the maximum size of the chunks that are sent to Kafka cluster. If it is not set, then the default value that will be used is 1MB.

Moreover, the list of the supported files must be provided as regular expressions. For instance, to support a filename like `nfcapd.20171103140000`, you have to set:

    "supported_files" :["nfcapd.*"],
or

    "supported_files": ["nfcapd.[0-9]{14}"],


### Installation
Installation requires a user with `sudo` privileges. Enter `spot-ingest` directory and run:
<br />`./install_DC.sh`

If you prefer to install the Distributed Collector on a remote host, just copy `spot-ingest` folder to the remote host and run the above installation file. It is important to mention that the remote host should have access to the Kafka cluster to work properly.


### Getting Started

**Start Distributed Collector**<br />
Enable the virtual environment
<br />`source venv/bin/activate`

and check the usage message of the Distributed Collector.

    python collector.py --help
    usage: Distributed Collector Daemon of Apache Spot [-h] [-c] [-l]
                                                       [--skip-conversion] --topic
                                                       TOPIC -t {dns,flow,proxy}

    optional arguments:
      -h, --help            show this help message and exit
      -c , --config-file    path of configuration file
      -l , --log-level      determine the level of the logger
      --skip-conversion     no transformation will be applied to the data; useful
                            for importing CSV files

    mandatory arguments:
      --topic TOPIC         name of topic where the messages will be published
      -t {dns,flow,proxy}, --type {dns,flow,proxy}
                            type of data that will be collected

    END

By default, it loads `ingest_conf.json` file. Using `-c , --config-file` option you can override it and use another.

Distributed Collector does not create a new topic, so you have to pass an existing one.

To start Distributed Collector:<br />
`python collector.py -t "pipeline_configuration" --topic "my_topic"`

Some examples are given below:<br />
1. `python collector.py -t flow --topic SPOT-INGEST-TEST-TOPIC`<br />
2. `python collector.py -t flow --topic SPOT-INGEST-TEST-TOPIC --config-file /tmp/another_ingest_conf.json`<br />
3. `python collector.py -t proxy --topic SPOT-PROXY-TOPIC --log-level DEBUG`<br />

**Start Streaming Listener**<br />
Print usage message and check the available options.

    python start_listener.py --help
    usage: Start Spark Job for Streaming Listener Daemon [-h] [-c] [-d] [-g] [-m]
                                                     [-n] [-r] -p PARTITIONS
                                                     -t {dns,flow,proxy}
                                                     --topic TOPIC

    optional arguments:
      -h, --help            show this help message and exit
      -c , --config-file    path of configuration file
      -d , --deploy-mode    Whether to launch the driver program locally
                            ("client") or on one of the worker machines inside the
                            cluster ("cluster")
      -g , --group-id       name of the consumer group to join for dynamic
                            partition assignment
      -l , --log-level      determine the level of the logger
      -m , --master         spark://host:port, mesos://host:port, yarn, or local
      -n , --app-name       name of the Spark Job to display on the cluster web UI
      -r , --redirect-spark-logs 
                            redirect output of spark to specific file

    mandatory arguments:
      -p PARTITIONS, --partitions PARTITIONS
                            number of partitions to consume; each partition is
                            consumed in its own thread
      -t {dns,flow,proxy}, --type {dns,flow,proxy}
                            type of the data that will be ingested
      --topic TOPIC         topic to listen for new messages

    END

By default, it loads `ingest_conf.json` file. Using `-c , --config-file` option you can override it and use another.

Streaming Listener uses `spark-streaming` parameters from the configuration file:

    "spark-streaming":{
        "driver_memory":"",
        "spark_exec":"",
        "spark_executor_memory":"",
        "spark_executor_cores":"",
        "spark_batch_size":""

The `spark_batch_size` is the time interval (in seconds) at which streaming data will be divided into batches. The default value is 30 seconds.

You can apply a Spark job on local, client or in cluster mode (using `-m , --master` and `-d , --deploy-mode` options).

Additionaly, you can isolate the logs from Spark, using the option `-r , --redirect-spark-logs`. This is usefull in case of debugging.

To start Streaming Listener:<br />
`python start_listener.py -t "pipeline_configuration" --topic "my_topic" -p "number of partitions to consume"`

Some examples are given below:<br />
1. `python start_listener.py -t flow --topic SPOT-INGEST-TOPIC -p 3 -g CUSTOM-GROUP-ID -n myApplication`<br />
2. `python start_listener.py -t flow --topic SPOT-INGEST-TOPIC -p 1 --master yarn --deploy-mode cluster`<br />
3. `python start_listener.py -t dns --topic SPOT-INGEST-DNS-TEST-TOPIC -p 4 --redirect-spark-logs /tmp/StreamingListener_Spark.log`<br />
