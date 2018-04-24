-- Licensed to the Apache Software Foundation (ASF) under one or more
-- contributor license agreements.  See the NOTICE file distributed with
-- this work for additional information regarding copyright ownership.
-- The ASF licenses this file to You under the Apache License, Version 2.0
-- (the "License"); you may not use this file except in compliance with
-- the License.  You may obtain a copy of the License at
--    http://www.apache.org/licenses/LICENSE-2.0
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

SET hiveconf:huser;
SET hiveconf:dbname;

CREATE EXTERNAL TABLE IF NOT EXISTS ${hiveconf:dbname}.ids_packet (
    data         STRING,
    event_id     INT,
    event_second INT,
    length       INT,
    linktype     TINYINT,
    sensor_id    INT,
    unix_tstamp  FLOAT
) PARTITIONED BY (
    y            SMALLINT,
    m            TINYINT,
    d            TINYINT,
    h            TINYINT
) STORED AS PARQUET LOCATION '${hiveconf:huser}/ids_packet/hive';
