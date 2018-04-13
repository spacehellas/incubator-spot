Spot Ingest Framework
========================================================================================================================================
Ingested data is captured or transferred into the Hadoop cluster, where they are transformed and loaded into solution data stores.

![Ingest Framework Architecture](../docs/SPOT_Ingest_Framework1_1.png)

## Ingestion using Spark Streaming
A new functionality is now available where the Distributed Collector transmits to Kafka cluster already processed files in a comma-separated (CSV) output format. Each row of the CSV corresponds to a table row in the Hive database. As a result, the Streaming Worker consumes batches of CSV messages from the Kafka cluster and registers them in Hive database.

**Distributed Collector**
<br />
The role of the Distributed Collector is similar, as it processes the data before transmission. Distributed Collector tracks a directory backwards for newly created files. When a file is detected, it converts it into CSV format and stores the output in the local staging area. Following to that, reads the CSV file line-by-line and creates smaller chunks of bytes. The size of each chunk depends on the maximum request size allowed by Kafka. Finally, it serializes each chunk into an Avro-encoded format and publishes them to Kafka cluster.<br />
Due to its architecture, Distributed Collector can run **on an edge node** of the Big Data infrastructure as well as **on a remote host** (proxy server, vNSF, etc).<br />
In addition, option `--skip-conversion` has been added. When this option is enabled, Distributed Collector expects already processed files in the CSV format. Hence, when it detects one, it does not apply any transformation; just splits it into chunks and transmits to the Kafka cluster.<br />
This option is also useful, when a segment failed to transmit to the Kafka cluster. By default, Distributed Collector stores the failed segment in CSV format under the local staging area. Then, using `--skip-conversion` option could be reloaded and sent to the Kafka cluster.<br />
Distributed Collector publishes to Apache Kafka only the CSV-converted file, and not the original one. The binary file remains to the local filesystem of the current host.

**Streaming Worker**
<br />
In contrary, Streaming Worker can only run on the central infrastructure. Its ability is to listen to a specific Kafka topic and consumes incoming messages. Streaming data is divided into batches (according to a time interval). These batches are deserialized by the Worker, according to the supported Avro schema, parsed and registered in the corresponding table of Hive.
