#!/bin/sh
. /etc/spot.conf

hdfs dfs -mkdir ${HUSER}/ids_event
hdfs dfs -mkdir ${HUSER}/ids_event/binary
hdfs dfs -mkdir ${HUSER}/ids_event/hive
hdfs dfs -mkdir ${HUSER}/ids_event/stage

hdfs dfs -mkdir ${HUSER}/ids_packet
hdfs dfs -mkdir ${HUSER}/ids_packet/binary
hdfs dfs -mkdir ${HUSER}/ids_packet/hive
hdfs dfs -mkdir ${HUSER}/ids_packet/stage
 
hive -hiveconf huser=${HUSER} -hiveconf dbname=${DBNAME} -f ../hive/create_ids_event_parquet.hql
hive -hiveconf huser=${HUSER} -hiveconf dbname=${DBNAME} -f ../hive/create_ids_packet_parquet.hql
