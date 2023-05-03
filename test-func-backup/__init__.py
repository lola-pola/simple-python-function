import os
import json
import datetime
import logging
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

def main(mytimer: func.TimerRequest, inputBlob: func.InputStream):
    try:
        logging.info('Python timer trigger function ran at %s', datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'))

        # Load configuration from input blob
        config = json.load(inputBlob)

        # Authenticate with Azure using default credentials
        credential = DefaultAzureCredential()
        # subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
        subscription_id = "564b567a-e4c8-4f24-b820-1ebf14319aac"
        compute_client = ComputeManagementClient(credential, subscription_id)

        # Get list of snapshots with specified tags
        snapshot_list = compute_client.snapshots.list()
        target_snapshots = []
        for snapshot in snapshot_list:
            if all(tag in snapshot.tags for tag in config['tags']):
                target_snapshots.append(snapshot)

        # Delete any excess snapshots
        if len(target_snapshots) > config['num_to_keep']:
            excess_snapshots = sorted(target_snapshots, key=lambda s: s.time_created)[:-(config['num_to_keep'])]
            for snapshot in excess_snapshots:
                compute_client.snapshots.begin_delete(snapshot.id)
                logging.info('Deleted snapshot %s', snapshot.name)
    except Exception as Error:
        print(f'{Error}')