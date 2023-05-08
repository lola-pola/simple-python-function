import os
import json
import datetime
import logging
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

def main(mytimer: func.TimerRequest, inputBlob: func.InputStream):
    try:
        import os
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.compute import ComputeManagementClient
        from azure.mgmt.storage import StorageManagementClient


        # Set the tag and the maximum number of snapshots to keep per disk
        tag_name = 'k8s-azure-created-by'
        tag_value = 'kubernetes-azure-dd'
        max_snapshots_per_disk = 120

        # Set your Azure subscription ID, resource group name, and region
        # subscription_id = "613ad620-f6ee-4055-bd0a-68a93656bee3"
        subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
        # Authenticate with the Azure management API using the default credentials
        credential = DefaultAzureCredential()
        compute_client = ComputeManagementClient(credential,subscription_id)

        # Get a list of all disks with the specified tag
        disks = compute_client.disks.list()
        # tagged_disks = [d for d in disks if tag_name in d.tags and d.tags[tag_name] == tag_value]
        tagged_disks = disks
        for disk in tagged_disks:
            try:
            ### create snapshot
                    snapshot_name = f'{disk.name}-snapshot-1'
                    print(f"create snapshot {snapshot_name} in resource group {disk.id.split('/')[4]}")
                    async_snapshot_creation = compute_client.snapshots.begin_create_or_update(
                    disk.id.split('/')[4], # this is the resource group name
                    snapshot_name, # this is the snapshot name

                    {
                        'location': disk.location, # this is the location of the disk
                        'incremental': 'true', # this enables incremental snapshots
                        'creation_data': { 
                            'incremental': 'true', # this enables incremental snapshots
                            'create_option': 'Copy', 
                            'source_uri': disk.id # this is the disk ID
                        }
                    }
                    )
                    try:
                        snapshot = async_snapshot_creation.result()
                    except Exception as Error:
                        pass
            except Exception as Erorr:
                pass
            snapshots = list(compute_client.snapshots.list())
            snapshots.sort(key=lambda s: s.time_created, reverse=True)
            for i, snapshot in enumerate(snapshots):
                if i >= max_snapshots_per_disk:
                    snap = snapshot.id.split('/')[4]
                    print(f"deleting snapshot resource group {snap}")
                    print(f"deleting snapshot {snapshot.name}")
                    compute_client.snapshots.begin_delete(resource_group_name=snap,snapshot_name=snapshot.name)
                else:
                    try:
                        snapshot_name = f'{disk.name}-snapshot-{i+1}'
                        print(f"create snapshot {snapshot_name} in resource group {disk.id.split('/')[4]}")
                        async_snapshot_creation = compute_client.snapshots.begin_create_or_update(
                        disk.id.split('/')[4],
                        snapshot_name,

                        {
                            'location': disk.location,
                            'incremental': 'true',
                            'creation_data': {
                                'incremental': 'true',
                                'create_option': 'Copy',
                                'source_uri': disk.id
                            }
                        }
                        )


                        snapshot = async_snapshot_creation.result()
                    except Exception as Error:
                        pass
        
        return func.HttpResponse(
             "This HTTP triggered {Error}",
             status_code=200
        )            
    except Exception as Error:
        return func.HttpResponse(
             "This HTTP triggered {Error}",
             status_code=200
        )




    