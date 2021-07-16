import json
import subprocess

from generate_metadata import MEDICAL_CLAIMS_PIPELINE, USERS, DELIVERY_MCES, DATA_PROCESSES

METADATA_FILE = 'examples/hv-demo/data/demo.json'


def ingest_metadata(payload):
    jsonFile = open("examples/hv-demo/data/demo.json", "w")
    jsonFile.write(payload)
    jsonFile.close()
    # Need to use compiled datahub binary to use metadata extensions
    out = subprocess.getoutput('venv/bin/datahub ingest -c ./examples/hv-demo/recipes/demo_to_datahub.yml')
    print(out)

# # Metadata population
#
# Emit metadata for USERS
input("\nIngest metadata for users")
ingest_metadata(json.dumps(USERS))


# Emit metadata for MEDICAL_CLAIMS_PIPELINE
for batch_id in MEDICAL_CLAIMS_PIPELINE:
    input(f"\nInitialize Datahub with a complete medical_claims dataset journey for batchId={batch_id}, orgId=5 ...")
    for stage in MEDICAL_CLAIMS_PIPELINE[batch_id]:
        input(f"Sending metadata for {stage} ...")
        jsonString = json.dumps(MEDICAL_CLAIMS_PIPELINE[batch_id][stage])
        ingest_metadata(jsonString)
    input()

# Emit metadata for Delivery Example
input("\nIngest metadata for delivery example")
ingest_metadata(json.dumps(DELIVERY_MCES))
ingest_metadata(json.dumps(DATA_PROCESSES))


import time
import json

from subprocess import check_output
from typing import List, Dict, Any
from datetime import datetime

import es_utils


NOW = 1612901777


# SCENARIO 1: Set matching priority based on deid file size
def get_file_size(dataset_urn: str):
    input("Sending file size metadata request to datahub...")
    res = es_utils.issue_search_query(
        es_utils.DATASET_INDEX,
        {
            "query": {
                "term": { "urn": dataset_urn }
            }
        }
    )
    print(res["hits"]["hits"][0]["_source"])
    return res["hits"]["hits"][0]["_source"]["fileSize"]

def set_matching_priority(dataset_urn: str) -> int:
    input(f"Deid file URN: {dataset_urn}")
    file_size = int(get_file_size(dataset_urn))
    input(f"File size pulled from metadata: {file_size} Mb")
    priority = "priority3"
    if file_size <= 100:
        priority = "priority1"
    elif file_size <= 500:
        priority = "priority2"
    else:
        priority = "prority3"
    input(f"Setting priority to {priority}")


# SCENARIO 2: Get the names of all the files from org 10, batch_id 5678 which arrived yesterday
def get_all_files_arrived(feed_type: str, org_id: str = None, batch_id: str = None, within_hours: int = 24) -> List[str]:

    yesterday = NOW - (within_hours * 60 * 60)

    clauses = [
        es_utils.create_range_clause(key='dateCreated', gte=yesterday, lte=NOW)
    ]

    if feed_type:
        clauses.append(es_utils.create_terms_clause(key='feedType', value=[feed_type]))
    if org_id:
        clauses.append(es_utils.create_terms_clause(key='orgId', value=[org_id]))
    if batch_id:
        clauses.append(es_utils.create_terms_clause(key='batchId', value=[batch_id]))

    res = es_utils.issue_search_query(
        es_utils.DATASET_INDEX,
        es_utils.create_search_query(clauses=clauses)
    )

    files = []
    for hit in res["hits"]["hits"]:
        s3_path = hit["_source"]["url"]
        arrival_date_timestamp = hit["_source"]["dateCreated"]
        timestamp = datetime.fromtimestamp(arrival_date_timestamp)
        print(f"{s3_path}		{timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        files.append(s3_path)
    input(f"Total num files: {len(files)}")
    return files


# SCENARIO 3: Get the data profile of a hive view, and set EMR cluster size based on number of rows

def load_data_profile_from_file(s3_file):
    # Mocks out s3 call to get data profile json
    hive_urn = "urn:li:dataset:(urn:li:dataPlatform:hive,dw.medical_claims,PROD)"
    return {
        "report_name": s3_file,
        "num_rows": 1000000 if s3_file == hive_urn else 1000,
        "num_columns": 10,
        "creation_date": "2021-02-09",
        "num_warnings": 5,
        "variables": [
            {
                "col_name": "hvid",
                "distinct_count": 1000000 if s3_file == hive_urn else 1000,
                "unique_pct": 100,
                "fill_rate": 100
            }
        ]
    }


def get_data_profile(dataset_urn: str) -> str:
    res = es_utils.issue_search_query(
        es_utils.DATASET_INDEX,
        {
            "query": {
                "term": { "urn": dataset_urn }
            }
        }
    )
    return res["hits"]["hits"][0]["_source"]["dataProfileUrl"]


def get_num_rows(dataset_urn: str) -> int:
    profile_url = get_data_profile(dataset_urn)
    input(f"Data profile URL pulled from metadata: {profile_url}")
    profile = load_data_profile_from_file(dataset_urn)
    input("Loading data profile contents...")
    input(json.dumps(profile, indent=4, sort_keys=True))
    return profile["num_rows"]


def make_decision_based_on_profile(dataset_urn: str):
    input(f"\nRequesting data profile URL metadata from datahub for {dataset_urn} ...")
    num_rows = get_num_rows(dataset_urn)
    input(f"Num rows pulled from data profile: {num_rows}")
    if num_rows <= 1000:
        input("Launching SMALL EMR Cluster...")
    elif num_rows <= 5000:
        input("Launching MEDIUM EMR Cluster...")
    else:
        input("Launching LARGE EMR Cluster...")


# SCENARIO 4: Get all datasets owned by userA and transfer ownership to userB
def emit_relationship_metadata_events(dataset_urns: List[str], user):
    new_owner_urn = f"urn:li:corpuser:{user}"
    mce_list = []
    for dataset_urn in dataset_urns:
        mce_list.append({
            "auditHeader": None,
            "proposedSnapshot": (
                "com.linkedin.pegasus2avro.metadata.snapshot.DatasetSnapshot",
                {
                    "urn": dataset_urn,
                    "aspects": [
                        (
                            "com.linkedin.pegasus2avro.common.Ownership",
                            {
                                # Overwrites old ownership aspect completely, to selectively override, need to implement
                                # with custom logic or look into modeling it as a datahub delta aspect.
                                "owners": [
                                    {"owner": new_owner_urn, "type": "DATAOWNER"},
                                    {"owner": "urn:li:corpuser:cflory", "type": "DATAOWNER"}
                                ],
                                "lastModified": {"time": 1581407189000, "actor": "urn:li:corpuser:jdoe"}
                            }
                        )
                    ]
                }
            ),
            "proposedDelta": None
        })
    # produce_from_list(events=mce_list)

# Scenario 5: Get details of the normalization runtime parameters used for orgId=5, batchId=1234
def get_normalization_runtime_details(output_urn):
    clauses = [
        es_utils.create_match_clause(key='outputs', value=output_urn)
    ]
    res = es_utils.issue_search_query(
        es_utils.DATAPROCESS_INDEX,
        es_utils.create_search_query(clauses=clauses)
    )
    details = res["hits"]["hits"][0]["_source"]
    # TODO: Break up.

    input("> What was the data process used for this extract?")

    print_fields = ["urn", "orchestrator"]
    for field in print_fields:
        print(f"{field}: {details[field]}")

    input()
    norm_fields = ["normalizationRoutine", "normalizationRoutineVersion", "normalizationRoutineArgs"]
    input("\n> What were the normalization runtime parameters used for this extract?")
    for field in norm_fields:
        print(f"{field}: {details[field]}")

    input()
    input("\n> What were the source datasets?")
    for i in details["inputs"]:
        print(i)

    input()
    input("\n> What were the output datasets?")
    for output in details["outputs"]:
        print(output)

def get_datasets_by_owner(user: str):
    clauses = [
        es_utils.create_match_clause(key='owners', value=user)
    ]
    res = es_utils.issue_search_query(
        es_utils.DATASET_INDEX,
        es_utils.create_search_query(clauses=clauses)
    )

    datasets = []
    for hit in res["hits"]["hits"]:
        print(hit["_source"]["urn"])
        datasets.append(hit["_source"]["urn"])
    return datasets


def transfer_ownership(source_user: str, dest_user: str):

    input(f"Datasets currently owned by source user {source_user} ...")
    datasets_owned_by_source_user = get_datasets_by_owner(source_user)
    input(f"Total: {len(datasets_owned_by_source_user)}")

    input(f"\nDatasets currently owned by dest user {dest_user} BEFORE ownership change ...")
    datasets_owned_by_dest_user = get_datasets_by_owner(dest_user)
    input(f"Total: {len(datasets_owned_by_dest_user)}")

    input("\nSending ownership change metadata events to Datahub ...")
    emit_relationship_metadata_events(datasets_owned_by_source_user, dest_user)

    time.sleep(5)

    input(f"\nDatasets owned by dest user {dest_user} AFTER ownership change ...")
    datasets_owned_by_dest_user = get_datasets_by_owner(dest_user)
    input(f"Total: {len(datasets_owned_by_dest_user)}")

    input(f"\nDatasets currently owned by source user {source_user} AFTER ownership change ...")
    datasets_owned_by_source_user = get_datasets_by_owner(source_user)
    input(f"Total: {len(datasets_owned_by_source_user)}")

def get_schedule_a(opp_id: str):
    # Canned for now - need to add institutional memory to dataset document search index.
    input("https://googledocs/hv001234/scheduleA.pdf")


def get_owners(opp_id: str):
    urn = "urn:li:dataset:(urn:li:dataPlatform:deliveries,HV001234,PROD)"
    clauses = [
        es_utils.create_match_clause(key='urn', value=urn)
    ]
    res = es_utils.issue_search_query(
        es_utils.DATASET_INDEX,
        es_utils.create_search_query(clauses=clauses)
    )

    owners = res["hits"]["hits"][0]["_source"]["owners"]
    input(owners)

def get_deliveries(opp_id: str):
    # clauses = [
    # 	es_utils.create_match_clause(key='opportunityId', value=opp_id)
    # ]
    # res = es_utils.issue_search_query(
    # 	es_utils.DATASET_INDEX,
    # 	es_utils.create_search_query(clauses=clauses)
    # )

    # delivery_dates = set()
    # for hit in res["hits"]["hits"]:
    # 	if "deliveryDate" in hit["_source"]:
    # 		delivery_dates.add(hit["_source"]["deliveryDate"])
    delivery_dates = (20210204, 20210211)
    input(str(delivery_dates))

def get_last_delivery(opp_id: str):
    # clauses = [
    # 	es_utils.create_match_clause(key='opportunityId', value=opp_id)
    # ]
    # res = es_utils.issue_search_query(
    # 	es_utils.DATASET_INDEX,
    # 	es_utils.create_search_query(clauses=clauses)
    # )

    # delivery_dates = set()
    # for hit in res["hits"]["hits"]:
    # 	if "deliveryDate" in hit["_source"]:
    # 		delivery_dates.add(hit["_source"]["deliveryDate"])
    delivery_dates = (20210204, 20210211)
    input(sorted(delivery_dates)[-1])


def get_extract_runtime_details(opp_id: str, delivery_date: str):
    output_urn = "urn:li:dataset:(urn:li:dataPlatform:s3,salusv/projects/client/HV001234/delivery/20210211/medical_claims,PROD)"
    clauses = [
        es_utils.create_match_clause(key='outputs', value=output_urn)
    ]
    res = es_utils.issue_search_query(
        es_utils.DATAPROCESS_INDEX,
        es_utils.create_search_query(clauses=clauses)
    )

    details = res["hits"]["hits"][0]["_source"]

    input("\n> What was the data process used for this extract?")
    print_fields = ["urn", "orchestrator"]
    for field in print_fields:
        print(f"{field}: {details[field]}")

    input()
    input("\n> What were the zeppelin runtime parameters used for the extract?")
    for param in ["zeppelinNotebook", "zeppelinNotebookVersion", "zeppelinNotebookArgs"]:
        print(f"{param}: {details[param]}")

    input()
    input("\n> What were the source datasets?")
    for i in details["inputs"]:
        print(i)

    input()
    input("\n> What were the output datasets?")
    for output in details["outputs"]:
        print(output)



if __name__ == '__main__':
    # Demo Runner

    # Logistics, Integrations, Data Engineering ...

    # Demo 1
    input(f"{'*'*75}\nSCENARIO 1: Set matching priority based on deid file size\n{'*'*75}")

    set_matching_priority("urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/incoming/test_client/1234/deid_payload.csv,PROD)")
    input("\n")
    set_matching_priority("urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/incoming/test_client/5678/deid_payload.csv,PROD)")

    # Demo 2
    # input()
    # input(f"\n{'*'*75}\nSCENARIO 2: Get the s3 paths of files which arrived in the last 24 hours\n{'*'*75}")
    #
    # input(f"Current Timestamp {datetime.fromtimestamp(NOW).strftime('%Y-%m-%d %H:%M:%S')}")
    #
    # input("\nRequest: Get all files feed=medical_claims which have arrived in the last 24 hours")
    # get_all_files_arrived(feed_type="medical_claims")
    #
    # input("\nRequest: Get all files from feed=medical_claims and org_id=5 in the last 24 hours")
    # get_all_files_arrived(feed_type="medical_claims", org_id="5")
    #
    # input("\nRequest: Get all files from feed=medical_claims AND and org_id=5 AND batch_id=1234 in the last 24 hours")
    # get_all_files_arrived(feed_type="medical_claims", org_id="5", batch_id="1234")
    #
    # # Demo 3
    input()
    input(f"\n{'*'*75}\nSCENARIO 3: Get the data profile of a hive view, and determine EMR cluster size based on # rows\n{'*'*75}")

    # Large cluster
    make_decision_based_on_profile("urn:li:dataset:(urn:li:dataPlatform:hive,dw.medical_claims,PROD)")

    # Small cluster
    make_decision_based_on_profile("urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/staging/test_client/5678/claims.csv,PROD)")
    #
    # # Demo 4
    # input()
    # input(f"\n{'*'*75}\nSCENARIO 4: Get normalization runtime parameters for orgId=5, batchId=5678\n{'*'*75}")
    # get_normalization_runtime_details("urn:li:dataset:(urn:li:dataPlatform:s3,healthverity/transformed/test_client/5678/all.csv,PROD)")
    #
    # # Demo 5
    # input()
    # input(f"\n{'*'*75}\nSCENARIO 5: Get all datasets owned by cflory and add echoe as an owner\n{'*'*75}")
    # input()
    # # transfer_ownership(source_user="cflory", dest_user="echoe")
    #
    #
    # # Demo 5 - Data Delivery Scenarios
    #
    # input(f"\n{'*'*75}\nSCENARIO 6: Data Delivery\n{'*'*75}")
    #
    # input("Use datahub to get metadata for delivery HV-001234 ...")
    #
    # input("\n> Who are the owners of HV-001234?")
    # get_owners(opp_id="HV-001234")
    #
    # input("\n> What is the schedule A document for HV-001234?")
    # get_schedule_a(opp_id="HV-001234")
    #
    # input("\n> What are all the deliveries made against HV-001234?")
    # get_deliveries(opp_id="HV-001234")
    #
    # input("\n> What is the last delivery made against HV-001234?")
    # get_last_delivery(opp_id="HV-001234")
    #
    #
    # input("\nUse datahub metadata to audit most recent delivery (20210211) for HV-001234 ...")
    #
    # # Get the zeppelin runtime information (notebookId, version, params) for this extract
    # get_extract_runtime_details(opp_id="HV-001234", delivery_date="20210211")



# import datahub.emitter.mce_builder as builder
# from datahub.emitter.kafka_emitter import DatahubKafkaEmitter, KafkaEmitterConfig
#
# # Construct a lineage object.
# lineage_mce = builder.make_lineage_mce(
#     [
#         builder.make_dataset_urn("bigquery", "upstream1"),
#         builder.make_dataset_urn("bigquery", "upstream2"),
#     ],
#     builder.make_dataset_urn("bigquery", "downstream"),
# )
#
# # Create an emitter to DataHub's Kafka broker.
# emitter = DatahubKafkaEmitter(
#     KafkaEmitterConfig.parse_obj(
#         # This is the same config format as the standard Kafka sink's YAML.
#         {
#             "connection": {
#                 "bootstrap": "localhost:9092",
#                 "producer_config": {},
#                 "schema_registry_url": "http://localhost:8081",
#             }
#         }
#     )
# )
#
#
# # Emit metadata!
# def callback(err, msg):
#     if err:
#         # Handle the metadata emission error.
#         print("error:", err)
#
#
# emitter.emit_mce_async(lineage_mce, callback)
# emitter.flush()
