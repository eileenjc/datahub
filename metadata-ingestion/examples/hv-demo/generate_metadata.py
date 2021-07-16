import time
import mce_utils

USERS = []

MEDICAL_CLAIMS_PIPELINE = {
    "1234": {
        "raw": [],
        "staged": [],
        "transformed": [],
        "prod": [],
        "hive": [],
    },
    # includes remediation flow
    "5678": {
        "raw": [],
        "staged_timeout": [],
        "staged": [],
        "transformed": [],
        "prod": [],
        "hive": [],
    }
}

DELIVERY_MCES = []

DATA_PROCESSES = []

FILE_ARRIVAL_TS = 1612901598
BAD_MATCHING_OUTPUT_TS = 1612901650
STAGE_TS = 1612901698
TRANSFORMED_TS = 1612901798
STAGE_TS = 1612901898
PROD_TS = 1612901998
HIVE_TS = 1612902998
EXTRACT_TS = 1612903998


for user in [
    ("integrations", "Integrations", "integrations@healthverity.com", "Integrations"),
    ("cflory", "Cree Flory", "cflory@healthverity.com", "Director, Integrations"),
    ("logistics", "Logistics", "logistics@healthverity.com", "Logistics"),
    ("jilluminati", "Joe Illuminati", "jilluminati@healthverity.com", "Engineering Manager"),
    ("warehouse", "Data Warehouse", "data_warehouse@healthverity.com", "Data Warehouse"),
    ("jdoe", "John Doe", "jdoe@healthverity.com", "Data Engineer"),
    ("echoe", "Eileen Choe", "echoe@healthverity.com", "Software Engineer"),
    ("delivery", "Data Delivery", "delivery@healthverity.com", "Data Delivery Team"),
    ("fmelkumyan", "Fera Melkumyan", "fmelkumyan@healthverity.com", "Data Delivery Analyst")
]:
    USERS.append(mce_utils.create_user(user))

for batch_id, file_size in [("1234", 100), ("5678", 500)]:
    for data_type in ["claims", "service_lines", "deid_payload"]:
        MEDICAL_CLAIMS_PIPELINE[batch_id]["raw"].append(mce_utils.create_raw(batch_id, data_type, file_size, FILE_ARRIVAL_TS))
        MEDICAL_CLAIMS_PIPELINE[batch_id]["staged"].append(mce_utils.create_staged(batch_id, data_type, STAGE_TS))
    MEDICAL_CLAIMS_PIPELINE[batch_id]["transformed"].append(mce_utils.create_transformed(batch_id, TRANSFORMED_TS))
    MEDICAL_CLAIMS_PIPELINE[batch_id]["prod"].append(mce_utils.create_prod(batch_id, PROD_TS))
    MEDICAL_CLAIMS_PIPELINE[batch_id]["hive"].append(mce_utils.create_hive_view(batch_id, HIVE_TS))
MEDICAL_CLAIMS_PIPELINE[batch_id]["staged_timeout"].append(mce_utils.create_timedout_matching_output(STAGE_TS))


DATA_PROCESSES.append(mce_utils.create_data_job(
    name="urn:li:dataJob:(urn:li:dataFlow:(emr,pyspark,PROD),spark/providers/inovalon/medicalclaims/normalize.py)",
    inputs=[
        "urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/staging/test_client/5678/matching_output.SUCCESS.csv,PROD)",
        "urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/staging/test_client/5678/service_lines.csv,PROD)",
        "urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/staging/test_client/5678/claims.csv,PROD)"
    ],
    outputs=[
        "urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/transformed/test_client/5678/all.csv,PROD)"
    ],
    data_job_info={
        "name": "Inovalon Medical Claims Normalization",
        "description": "Normalizes medical claims",
        "type": "ZEPPELIN",
        "flowUrn": "urn:li:dataFlow:(emr,pyspark,PROD)",
    }
    # runtime_parameters={
    #     "normalizationRoutine": "spark/providers/inovalon/medicalclaims/normalize.py",
    #     "normalizationRoutineVersion": "8b0443e",  # commit hash
    #     "normalizationRoutineArgs": "--date 2020-02-02 --end_to_end_test",
    #     "runTimestamp": STAGE_TS
    # }
    )
)


# DATA_PROCESSES.append(mce_utils.create_data_process(
#     name="urn:li:dataProcess:(emr,spark/providers/inovalon/medicalclaims/normalize.py,PROD)",
#     inputs=[
#         "urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/staging/test_client/5678/matching_output.SUCCESS.csv,PROD)",
#         "urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/staging/test_client/5678/service_lines.csv,PROD)",
#         "urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/staging/test_client/5678/claims.csv,PROD)"
#     ],
#     outputs=[
#         "urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/transformed/test_client/5678/all.csv,PROD)"
#     ],
#     runtime_parameters={
#         "normalizationRoutine": "spark/providers/inovalon/medicalclaims/normalize.py",
#         "normalizationRoutineVersion": "8b0443e",  # commit hash
#         "normalizationRoutineArgs": "--date 2020-02-02 --end_to_end_test",
#         "runTimestamp": STAGE_TS
#     })
# )

DELIVERY_DATES = ["20210204", "20210211"]

def create_extracts(delivery_dates, ts):
    mces = []
    for delivery_date in delivery_dates:
        mces.append(
            # pharmacy claims extract
            mce_utils.create_general_dataset(
                urn= f"urn:li:dataset:(urn:li:dataPlatform:s3,salusv/projects/client/HV001234/delivery/{delivery_date}/pharmacy_claims,PROD)",
                ts = 1613069581,
                custom_properties={
                    "opportunityId": "HV-0001234",
                    "feedType": "pharmacy_claims",
                    "deliveryDate": str(delivery_date)
                },
                upstreams=[
                    {
                        "auditStamp": {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"},
                        "dataset": "urn:li:dataset:(urn:li:dataPlatform:hive,dw.pharmacy_claims,PROD)",
                        "type": "TRANSFORMED"
                    }
                ],
                owners=[
                    {"owner": "urn:li:corpuser:fmelkumyan", "type": "DATAOWNER"},
                    {"owner": "urn:li:corpuser:delivery", "type": "DATAOWNER"},
                ]

            )
        )
        mces.append(
            # medical claims extract
            mce_utils.create_general_dataset(
                urn= f"urn:li:dataset:(urn:li:dataPlatform:s3,salusv/projects/client/HV001234/delivery/{delivery_date}/medical_claims,PROD)",
                ts = 1613069581,
                custom_properties={
                    "opportunityId": "HV-0001234",
                    "feedType": "medical_claims",
                    "deliveryDate": str(delivery_date)
                },
                upstreams=[
                    {
                        "auditStamp": {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"},
                        "dataset": "urn:li:dataset:(urn:li:dataPlatform:hive,dw.medical_claims,PROD)",
                        "type": "TRANSFORMED"
                    }
                ],
                owners=[
                    {"owner": "urn:li:corpuser:fmelkumyan", "type": "DATAOWNER"},
                    {"owner": "urn:li:corpuser:delivery", "type": "DATAOWNER"},
                ]

            )
        )
        mces.append(

            mce_utils.create_data_job(
                name="urn:li:dataJob:(urn:li:dataFlow:(emr,notebookRunner,PROD),note_2FVBR216V)",
                inputs=[
                    "urn:li:dataset:(urn:li:dataPlatform:hive,cli123.patient_list,PROD)",
                    "urn:li:dataset:(urn:li:dataPlatform:hive,cli123.ndc_list,PROD)",
                    "urn:li:dataset:(urn:li:dataPlatform:hive,dw.pharmacy_claims,PROD)",
                    "urn:li:dataset:(urn:li:dataPlatform:hive,dw.medical_claims,PROD)"
                ],
                outputs=[
                    # rx extract
                    f"urn:li:dataset:(urn:li:dataPlatform:s3,salusv/projects/client/HV001234/delivery/{delivery_date}/pharmacy_claims,PROD)",
                    # dx extract
                    f"urn:li:dataset:(urn:li:dataPlatform:s3,salusv/projects/client/HV001234/delivery/{delivery_date}/medical_claims,PROD)"
                ],
                # Doesn't work, might need to add to the top level dataflow document
                data_job_info={
                    "name": "Notebook 2FVBR216V",
                    "description": "Extracts data for delivery",
                    "type": "ZEPPELIN",
                    "flowUrn": "urn:li:dataFlow:(emr,notebookRunner,PROD)",
                }
            )

            # # extract zeppelin data process
            # mce_utils.create_data_process(
            #     name="urn:li:dataProcess:(notebookRunner,2FVBR216V,PROD)",
            #     inputs=[
            #         "urn:li:dataset:(urn:li:dataPlatform:hive,cli123.patient_list,PROD)",
            #         "urn:li:dataset:(urn:li:dataPlatform:hive,cli123.ndc_list,PROD)",
            #         "urn:li:dataset:(urn:li:dataPlatform:hive,dw.pharmacy_claims,PROD)",
            #         "urn:li:dataset:(urn:li:dataPlatform:hive,dw.medical_claims,PROD)"
            #     ],
            #     outputs=[
            #         # rx extract
            #         f"urn:li:dataset:(urn:li:dataPlatform:s3,salusv/projects/client/HV001234/delivery/{delivery_date}/pharmacy_claims,PROD)",
            #         # dx extract
            #         f"urn:li:dataset:(urn:li:dataPlatform:s3,salusv/projects/client/HV001234/delivery/{delivery_date}/medical_claims,PROD)"
            #     ],
            #     runtime_parameters={
            #         "zeppelinNotebook": "2FVBR216V",
            #         "zeppelinNotebookVersion": "8b0443e",
            #         "zeppelinNotebookArgs": "delivery,dxstart,dxend,rxstart,rxend,enrollstart,enrollend,lxstart,lxend,emrstart,emrend 2021-02-25,2015-10-01,2021-02-25,2015-10-01,2021-02-25,2015-10-01,2021-02-25,2017-01-01,2021-02-25,2015-10-01,2021-02-25",
            #         "runTimestamp": ts
            #     }
            # )

        )
    return mces


def create_extract_views(delivery_dates):
    mces = []
    for delivery_date in delivery_dates:
        upstreams = [
            {
                "auditStamp": {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"},
                "dataset": f"urn:li:dataset:(urn:li:dataPlatform:s3,salusv/projects/client/HV001234/delivery/{delivery_date}/pharmacy_claims,PROD)",
                "type": "VIEW"
            },
            # dx extract
            {
                "auditStamp": {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"},
                "dataset": f"urn:li:dataset:(urn:li:dataPlatform:s3,salusv/projects/client/HV001234/delivery/{delivery_date}/medical_claims,PROD)",
                "type": "VIEW"
            },
            # ndc list - "urn:li:dataset:(urn:li:dataPlatform:hive,cli123.ndc_list,PROD)"
            {
                "auditStamp": {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"},
                "dataset": f"urn:li:dataset:(urn:li:dataPlatform:hive,cli123.ndc_list,PROD)",
                "type": "VIEW"
            },
            # patient list - "urn:li:dataset:(urn:li:dataPlatform:hive,cli123.patient_list,PROD)"
            {
                "auditStamp": {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"},
                "dataset": f"urn:li:dataset:(urn:li:dataPlatform:hive,cli123.patient_list,PROD)",
                "type": "VIEW"
            },
        ]
        mces.append(
            mce_utils.create_general_dataset(
                urn= f"urn:li:dataset:(urn:li:dataPlatform:extracts,HV001234/{delivery_date},PROD)",
                ts = 1613069581,
                custom_properties={
                    "opportunityId": "HV-0001234",
                },
                upstreams=upstreams,
                owners=[
                    {"owner": "urn:li:corpuser:fmelkumyan", "type": "DATAOWNER"},
                    {"owner": "urn:li:corpuser:delivery", "type": "DATAOWNER"},
                ]
            )
        )
    return mces



def create_delivery(delivery_dates):
    # delivery = medical claims + pharmacy claims extracts x 2
    upstreams = []
    for delivery_date in delivery_dates:
        upstreams.extend(
            [{
                "auditStamp": {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"},
                "dataset": f"urn:li:dataset:(urn:li:dataPlatform:extracts,HV001234/{delivery_date},PROD)",
                "type": "VIEW"
            },
                # dx extract
                {
                    "auditStamp": {"time": 1581407189000, "actor": "urn:li:corpuser:airflow"},
                    "dataset": f"urn:li:dataset:(urn:li:dataPlatform:extracts,HV001234/{delivery_date},PROD)",
                    "type": "VIEW"
                }
            ]
        )

    mce = mce_utils.create_general_dataset(
        urn= f"urn:li:dataset:(urn:li:dataPlatform:deliveries,HV001234,PROD)",
        ts = 1613069581,
        custom_properties={
            "opportunityId": "HV-0001234",
        },
        upstreams=upstreams,
        owners=[
            {"owner": "urn:li:corpuser:fmelkumyan", "type": "DATAOWNER"},
            {"owner": "urn:li:corpuser:delivery", "type": "DATAOWNER"},
        ],
        institutional_memory_elements=[
            {
                "url":"https://googledocs/hv001234/scheduleA.pdf",
                "description":"Schedule A for Opp ID HV-001234",
                "createStamp":{"time":1581407189000,"actor":"urn:li:corpuser:fmelkumyan"}
            }
        ]
    )
    return mce

DELIVERY_MCES.extend([
    # pharma claims table
    mce_utils.create_general_dataset(
        urn="urn:li:dataset:(urn:li:dataPlatform:hive,dw.pharmacy_claims,PROD)",
        ts=1613069581,
        custom_properties={
            "feedType": "pharmacy_claims",
            "dataProfileUrl": "s3://path/to/pharma/claims/profile.json"
        }
    ),

    # ndc list table
    mce_utils.create_general_dataset(
        urn="urn:li:dataset:(urn:li:dataPlatform:hive,cli123.ndc_list,PROD)",
        ts=1613069581,
        custom_properties={
            "opportunityId": "HV-0001234"
        }
    ),

    # patient list table
    mce_utils.create_general_dataset(
        urn="urn:li:dataset:(urn:li:dataPlatform:hive,cli123.patient_list,PROD)",
        ts=1613069581,
        custom_properties={
            "opportunityId": "HV-0001234"
        }
    ),
    *create_extracts(DELIVERY_DATES, EXTRACT_TS),
    *create_extract_views(DELIVERY_DATES),
    create_delivery(DELIVERY_DATES)
])
