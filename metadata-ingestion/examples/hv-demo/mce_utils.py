from typing import List


def create_data_job(name: str, inputs: List[str], outputs: List[str], data_job_info=None):
    return {
        "auditHeader": None,
        "proposedSnapshot": {
            "com.linkedin.pegasus2avro.metadata.snapshot.DataJobSnapshot":
                {
                    "urn": name,
                    "aspects": [
                        {
                            "com.linkedin.pegasus2avro.common.Ownership": {
                                "owners": [
                                    {
                                        "owner": "urn:li:corpuser:datahub",
                                        "type": "DATAOWNER",
                                        "source": None
                                    }
                                ],
                                "lastModified": {
                                    "time": 1581407189000,
                                    "actor": "urn:li:corpuser:datahub",
                                    "impersonator": None
                                }
                            }
                        },
                        {
                            "com.linkedin.pegasus2avro.datajob.DataJobInfo": {
                                **data_job_info
                            }
                        },
                        {
                            "com.linkedin.pegasus2avro.datajob.DataJobInputOutput":
                                {
                                    "inputDatasets": inputs,
                                    "outputDatasets": outputs,
                                }
                        }
                    ]
                }
        },
        "proposedDelta": None
    }


def create_data_process(name: str, inputs: List[str], outputs: List[str], runtime_parameters=None):
    return {
        "auditHeader": None,
        "proposedSnapshot": {
            "com.linkedin.pegasus2avro.metadata.snapshot.DataProcessSnapshot":
            {
                "urn": name,
                "aspects": [{
                    "com.linkedin.pegasus2avro.dataprocess.DataProcessInfo":
                    {
                        "inputs": inputs,
                        "outputs": outputs,
                        **runtime_parameters
                    }
                }]
            }
        },
        "proposedDelta": None
    }


def create_user(user):
    return {
        "auditHeader": None,
        "proposedSnapshot": {
            "com.linkedin.pegasus2avro.metadata.snapshot.CorpUserSnapshot":
            {
                "urn": f"urn:li:corpuser:{user[0]}",
                "aspects": [{
                    "com.linkedin.pegasus2avro.identity.CorpUserInfo":
                    {
                        "active": True,
                        "displayName": user[1],
                        "fullName": user[1],
                        "email": user[2],
                        "title": user[3]
                    }}
                ]
            }
        },
        "proposedDelta": None
    }


def create_timedout_matching_output(ts):
    return {
        "auditHeader": None,
        "proposedSnapshot": {
            "com.linkedin.pegasus2avro.metadata.snapshot.DatasetSnapshot":
            {
                "urn": "urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/staging/test_client/5678/matching_output.TIMEDOUT.csv,PROD)",
                "aspects": [
                    {
                        "com.linkedin.pegasus2avro.common.Ownership":
                        {
                            "owners": [
                                {"owner": "urn:li:corpuser:logistics", "type": "DATAOWNER"},
                                {"owner": "urn:li:corpuser:jilluminati", "type": "DATAOWNER"}
                            ],
                            "lastModified":
                                {"time": 1581407189000, "actor": "urn:li:corpuser:jdoe"}
                        }
                    },
                    {
                        "com.linkedin.pegasus2avro.dataset.DatasetProperties":
                        {
                            "customProperties": {
                                "batchId": "5678",
                                "orgId": "5",
                                "feedType": "medical_claims",
                                "dataProfileUrl": "s3://path/to/data_profile.json",
                                "url": "urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/staging/test_client/5678/matching_output.TIMEDOUT.csv,PROD)",
                                "fileSize": "0",
                                "version": "1",
                                "dateCreated": str(ts)
                            },
                            "batchId": "5678",
                            "orgId": "5",
                            "feedType": "medical_claims",
                            "dataProfileUrl": "s3://path/to/data_profile.json",
                            "url": "urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/staging/test_client/5678/matching_output.TIMEDOUT.csv,PROD)",
                            "fileSize": "0",  # no matching output
                            "version": "1",
                            "dateCreated": str(ts)
                        }
                    },
                    {
                        "com.linkedin.pegasus2avro.dataset.UpstreamLineage":
                        {
                            "upstreams": [
                                {
                                    "auditStamp": {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"},
                                    "dataset": f"urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/incoming/test_client/5678/deid_payload.csv,PROD)",
                                    "type": "TRANSFORMED",
                                    "normalizationRoutine": "https://github.com/healthverity/dewey/blob/master/spark/providers/liquidhub/custom/normalize.sql",
                                    "normalizationRoutineVersion": "2285eeb",  # github commit hash
                                    "normalizationRoutineArgs": "group_id=1234"
                                }
                            ]
                        }
                    },
                    {
                        "com.linkedin.pegasus2avro.dataset.DatasetDeprecation":
                        {
                            "deprecated": True,
                            "note": "Dataset was depreciated because matching timed out",
                            "actor": "urn:li:corpuser:cflory",
                            "decommissionTime": 1581407189000
                        }
                    },
                    {
                        "com.linkedin.pegasus2avro.common.Ownership":
                        {
                            "owners": [
                                {"owner": "urn:li:corpuser:warehouse", "type": "DATAOWNER"},
                                {"owner": "urn:li:corpuser:jdoe", "type": "DATAOWNER"}
                            ],
                            "lastModified":
                                {"time": 1581407189000, "actor": "urn:li:corpuser:jdoe"}
                        }
                    },
                ]
            }
        },
        "proposedDelta": None
    }

def create_staged(batch_id, data_type, ts):
    upstream = data_type

    if data_type == "deid_payload" and batch_id == "5678":
        data_type = "matching_output.SUCCESS"
    elif data_type == "deid_payload":
        data_type = "matching_output"

    version = 2 if (data_type == "deid_payload" and batch_id == "5678") else 1

    return {
        "auditHeader": None,
        "proposedSnapshot": {
            "com.linkedin.pegasus2avro.metadata.snapshot.DatasetSnapshot":
            {
                "urn": f"urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/staging/test_client/{batch_id}/{data_type}.csv,PROD)",
                "aspects": [
                    {
                        "com.linkedin.pegasus2avro.common.Ownership":
                        {
                            "owners": [
                                {"owner": "urn:li:corpuser:logistics", "type": "DATAOWNER"},
                                {"owner": "urn:li:corpuser:jilluminati", "type": "DATAOWNER"}
                            ],
                            "lastModified":
                                {"time": 1581407189000, "actor": "urn:li:corpuser:jdoe"}
                        }
                    },
                    {
                        "com.linkedin.pegasus2avro.dataset.DatasetProperties":
                        {
                            "customProperties": {
                                "batchId": batch_id,
                                "orgId": "5",
                                "feedType": "medical_claims",
                                "dataProfileUrl": "s3://path/to/data_profile.json",
                                "url": f"s3://healthverity/staging/test_client/{batch_id}/{data_type}.csv",
                                "fileSize": "500",
                                "version": "1",
                                "dateCreated": str(ts)
                            },
                            "batchId": batch_id,
                            "orgId": "5",
                            "feedType": "medical_claims",
                            "dataProfileUrl": "s3://path/to/data_profile.json",
                            "url": f"s3://healthverity/staging/test_client/{batch_id}/{data_type}.csv",
                            "fileSize": "500",
                            "version": str(version),
                            "dateCreated": str(ts)
                        }
                    },
                    {
                        "com.linkedin.pegasus2avro.dataset.UpstreamLineage":
                        {
                            "upstreams": [
                                {
                                    "auditStamp": {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"},
                                    "dataset": f"urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/incoming/test_client/{batch_id}/{upstream}.csv,PROD)",
                                    "type": "TRANSFORMED"
                                }
                            ]
                        }
                    },
                    {
                        "com.linkedin.pegasus2avro.common.Ownership":
                        {
                            "owners": [
                                {"owner": "urn:li:corpuser:warehouse", "type": "DATAOWNER"},
                                {"owner": "urn:li:corpuser:jdoe", "type": "DATAOWNER"}
                            ],
                            "lastModified":
                                {"time": 1581407189000, "actor": "urn:li:corpuser:jdoe"}
                        }
                    },
                ]
            }
        },
        "proposedDelta": None
    }

def create_raw(batch_id, data_type, file_size, file_arrival_ts):
    return {
        "auditHeader": None,
        "proposedSnapshot": {
            "com.linkedin.pegasus2avro.metadata.snapshot.DatasetSnapshot":
            {
                "urn": f"urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/incoming/test_client/{batch_id}/{data_type}.csv,PROD)",
                "aspects": [
                    {
                        "com.linkedin.pegasus2avro.common.Ownership":
                        {
                            "owners": [
                                {"owner": "urn:li:corpuser:integrations", "type": "DATAOWNER"},
                                {"owner": "urn:li:corpuser:cflory", "type": "DATAOWNER"}
                            ],
                            "lastModified":
                                {"time": 1581407189000, "actor": "urn:li:corpuser:jdoe"}
                        }
                    },
                    {"com.linkedin.pegasus2avro.dataset.DatasetProperties":
                     {
                         # Note: s3 URI cannot be coerced to type java.net.URI
                         # "uri": f"s3://healthverity/incoming/test_client/1234/{data_type}.csv",
                         "customProperties": {
                             "batchId": batch_id,
                             "orgId": "5",
                             "feedType": "medical_claims",
                             "dataProfileUrl": "s3://path/to/data_profile.json",
                             "url": f"s3://healthverity/incoming/test_client/{batch_id}/{data_type}.csv",
                             "fileSize": str(file_size),
                             "dateCreated": str(file_arrival_ts),  # custom property values can't be int
                             "version": "1"
                         },
                         "batchId": batch_id,
                         "orgId": "5",
                         "feedType": "medical_claims",
                         "dataProfileUrl": "s3://path/to/data_profile.json",
                         "url": f"s3://healthverity/incoming/test_client/{batch_id}/{data_type}.csv",
                         "fileSize": str(file_size),
                         "dateCreated": str(file_arrival_ts),
                         "version": "1"
                     }
                     }
                ]
            }
        },
        "proposedDelta": None
    }


def create_transformed(batch_id, ts):
    if batch_id == "5678":
        matching_output = f"urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/staging/test_client/{batch_id}/matching_output.SUCCESS.csv,PROD)"
    else:
        matching_output = f"urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/staging/test_client/{batch_id}/matching_output.csv,PROD)"

    return {
        "auditHeader": None,
        "proposedSnapshot": {
            "com.linkedin.pegasus2avro.metadata.snapshot.DatasetSnapshot":
            {
                "urn": f"urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/transformed/test_client/{batch_id}/all.csv,PROD)",
                "aspects": [
                    {
                        "com.linkedin.pegasus2avro.dataset.DatasetProperties":
                        {
                            "customProperties": {
                                "batchId": batch_id,
                                "orgId": "5",
                                "feedType": "medical_claims",
                                "dataProfileUrl": "s3://path/to/data_profile.json",
                                "url": f"s3://healthverity/transformed/test_client/{batch_id}/all.csv",
                                "fileSize": "500",
                                "version": "1",
                                "dateCreated": str(ts)
                            },
                            "batchId": batch_id,
                            "orgId": "5",
                            "feedType": "medical_claims",
                            "dataProfileUrl": "s3://path/to/data_profile.json",
                            "url": f"s3://healthverity/transformed/test_client/{batch_id}/all.csv",
                            "fileSize": "500",
                            "version": "1",
                            "dateCreated": str(ts)
                        }
                    },
                    {
                        "com.linkedin.pegasus2avro.dataset.UpstreamLineage":
                        {
                            "upstreams": [
                                {
                                    "auditStamp": {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"},
                                    "dataset": f"urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/staging/test_client/{batch_id}/claims.csv,PROD)",
                                    "type": "TRANSFORMED"
                                },
                                {
                                    "auditStamp": {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"},
                                    "dataset": f"urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/staging/test_client/{batch_id}/service_lines.csv,PROD)",
                                    "type": "TRANSFORMED"
                                },
                                {
                                    "auditStamp": {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"},
                                    "dataset": matching_output,
                                    "type": "TRANSFORMED"
                                },
                            ]
                        }
                    }
                ]
            }
        },
        "proposedDelta": None
    }

def create_prod(batch_id, ts):
    return {
        "auditHeader": None,
        "proposedSnapshot": {
            "com.linkedin.pegasus2avro.metadata.snapshot.DatasetSnapshot":
            {
                "urn": f"urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/prod/test_client/{batch_id}/out.csv,PROD)",
                "aspects": [
                    {
                        "com.linkedin.pegasus2avro.dataset.DatasetProperties":
                        {
                            "customProperties": {
                                "batchId": batch_id,
                                "orgId": "5",
                                "feedType": "medical_claims",
                                "dataProfileUrl": "s3://path/to/data_profile.json",
                                "url": f"s3://healthverity/prod/test_client/{batch_id}/out.csv",
                                "fileSize": "500",
                                "version": "1",
                                "dateCreated": str(ts)
                            },
                            "batchId": batch_id,
                            "orgId": "5",
                            "feedType": "medical_claims",
                            "dataProfileUrl": "s3://path/to/data_profile.json",
                            "url": f"s3://healthverity/prod/test_client/{batch_id}/out.csv",
                            "fileSize": "500",
                            "version": "1",
                            "dateCreated": str(ts)
                        }
                    },
                    {
                        "com.linkedin.pegasus2avro.dataset.UpstreamLineage":
                        {
                            "upstreams": [
                                {
                                    "auditStamp": {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"},
                                    "dataset": f"urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/transformed/test_client/{batch_id}/all.csv,PROD)",
                                    "type": "COPY"
                                }
                            ]
                        }
                    },
                    {
                        "com.linkedin.pegasus2avro.common.Ownership":
                        {
                            "owners": [
                                {"owner": "urn:li:corpuser:warehouse", "type": "DATAOWNER"},
                                {"owner": "urn:li:corpuser:jdoe", "type": "DATAOWNER"}
                            ],
                            "lastModified":
                                {"time": 1581407189000, "actor": "urn:li:corpuser:jdoe"}
                        }
                    },
                ]
            }
        },
        "proposedDelta": None
    }


def create_hive_view(batch_id, ts):
    upstreams = [
        {
            "auditStamp": {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"},
            "dataset": f"urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/prod/test_client/{batch_id}/out.csv,PROD)",
            "type": "VIEW"
        }
    ]
    if batch_id == "5678":
        upstreams.append(
            {
                "auditStamp": {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"},
                "dataset": f"urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/prod/test_client/1234/out.csv,PROD)",
                "type": "VIEW"
            }
        )
    return {
        "auditHeader": None,
        "proposedSnapshot": {
            "com.linkedin.pegasus2avro.metadata.snapshot.DatasetSnapshot":
            {
                "urn": "urn:li:dataset:(urn:li:dataPlatform:hive,dw.medical_claims,PROD)",
                "aspects": [
                    {
                        "com.linkedin.pegasus2avro.dataset.DatasetProperties":
                        {
                            "customProperties": {
                                "feedType": "medical_claims",
                                "dataProfileUrl": "s3://path/to/data_profile.json",
                                "dateCreated": str(ts)
                            },
                            "feedType": "medical_claims",
                            "dataProfileUrl": "s3://path/to/data_profile.json",
                            "dateCreated": ts
                        }
                    },
                    {
                        "com.linkedin.pegasus2avro.dataset.UpstreamLineage":
                        {
                            "upstreams": upstreams
                        }
                    },
                    {
                        "com.linkedin.pegasus2avro.common.Ownership":
                        {
                            "owners": [
                                {"owner": "urn:li:corpuser:warehouse", "type": "DATAOWNER"},
                                {"owner": "urn:li:corpuser:jdoe", "type": "DATAOWNER"}
                            ],
                            "lastModified":
                                {"time": 1581407189000, "actor": "urn:li:corpuser:jdoe"}
                        }
                    },
                    {
                        "com.linkedin.pegasus2avro.schema.SchemaMetadata":
                        {
                            "schemaName": "SampleHiveSchema",
                            "platform": "urn:li:dataPlatform:hive",
                            "version": 0,
                            "created": {"time": 1581407189000, "actor": "urn:li:corpuser:jdoe"},
                            "lastModified": {"time": 1581407189000, "actor": "urn:li:corpuser:jdoe"},
                            "hash": "",
                            "platformSchema": {
                                "documentSchema": "{\"type\":\"record\",\"name\":\"SampleHiveSchema\",\"namespace\":\"com.linkedin.dataset\",\"doc\":\"Sample Hive dataset\",\"fields\":[{\"name\":\"field_foo\",\"type\":[\"string\"]},{\"name\":\"field_bar\",\"type\":[\"boolean\"]}]}"
                            },
                            "fields": [
                                {
                                    "fieldPath": "field_foo",
                                    "description": "Foo field description",
                                    "nativeDataType": "string",
                                    "type": {"type": {"com.linkedin.pegasus2avro.schema.StringType": {}}}
                                },
                                {
                                    "fieldPath": "field_bar",
                                    "description": "Bar field description",
                                    "nativeDataType": "boolean",
                                    "type": {"type": {"com.linkedin.pegasus2avro.schema.BooleanType": {}}}
                                }
                            ]
                        }
                    }
                ]
            }
        },
        "proposedDelta": None
    }


def create_general_dataset(urn, ts, custom_properties, owners=None, upstreams=None, institutional_memory_elements=None):
    aspects = [
        {
            "com.linkedin.pegasus2avro.dataset.DatasetProperties":
            {
                "customProperties": {
                    **custom_properties,
                    "dateCreated": str(ts)
                },
                **custom_properties,
                "dateCreated": ts
            }
        },
        {
            "com.linkedin.pegasus2avro.schema.SchemaMetadata":
            {
                "schemaName": "SampleHiveSchema",
                "platform": "urn:li:dataPlatform:hive",
                "version": 0,
                "created": {"time": 1581407189000, "actor": "urn:li:corpuser:jdoe"},
                "lastModified": {"time": 1581407189000, "actor": "urn:li:corpuser:jdoe"},
                "hash": "",
                "platformSchema": {
                    "documentSchema": "{\"type\":\"record\",\"name\":\"SampleHiveSchema\",\"namespace\":\"com.linkedin.dataset\",\"doc\":\"Sample Hive dataset\",\"fields\":[{\"name\":\"field_foo\",\"type\":[\"string\"]},{\"name\":\"field_bar\",\"type\":[\"boolean\"]}]}"
                },
                "fields": [
                    {
                        "fieldPath": "field_foo",
                        "description": "Foo field description",
                        "nativeDataType": "string",
                        "type": {"type": {"com.linkedin.pegasus2avro.schema.StringType": {}}}
                    },
                    {
                        "fieldPath": "field_bar",
                        "description": "Bar field description",
                        "nativeDataType": "boolean",
                        "type": {"type": {"com.linkedin.pegasus2avro.schema.BooleanType": {}}}
                    }
                ]
            }
        }
    ]

    if upstreams:
        aspects.append(
            {
                "com.linkedin.pegasus2avro.dataset.UpstreamLineage":
                {
                    "upstreams": upstreams
                }
            }
        )

    if owners:
        aspects.append(
            {
                "com.linkedin.pegasus2avro.common.Ownership":
                {
                    "owners": owners,
                    "lastModified":
                        {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"}
                }
            }
        )

    if institutional_memory_elements:
        aspects.append(
            {
                "com.linkedin.pegasus2avro.common.InstitutionalMemory":
                {
                    "elements": institutional_memory_elements
                }
            }
        )

    return {
        "auditHeader": None,
        "proposedSnapshot": {
            "com.linkedin.pegasus2avro.metadata.snapshot.DatasetSnapshot":
            {
                "urn": urn,
                "aspects": aspects
            }
        },
        "proposedDelta": None
    }
