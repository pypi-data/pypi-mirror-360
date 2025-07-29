import re
import time
import pydcgm
import dcgm_structs
import dcgm_fields
import pandas as pd
from .cmd_util import exec_cmd

__all__ = [
    "dcgm_monitor_mig_resource",
    "dcgm_monitor_gpu_resource"
]

REGISTER_FIELD_IDS = [
    dcgm_fields.DCGM_FI_PROF_GR_ENGINE_ACTIVE,
    dcgm_fields.DCGM_FI_PROF_SM_ACTIVE,
    dcgm_fields.DCGM_FI_PROF_SM_OCCUPANCY,
    dcgm_fields.DCGM_FI_DEV_FB_TOTAL,
    dcgm_fields.DCGM_FI_DEV_FB_FREE,
    dcgm_fields.DCGM_FI_DEV_FB_USED,
    dcgm_fields.DCGM_FI_DEV_FB_RESERVED,
]

CSV_HEADER = [
    "gpu_util",
    "sm_active",
    "sm_occupancy",
    "mem_total",
    "mem_free",
    "mem_used",
    "mem_reserved",
]


def _getEntityId(gpu_id, gi_id, ci_id):
    dcgmi_cmd = "dcgmi discovery -c"
    exit_status, out = exec_cmd(dcgmi_cmd)
    if exit_status != 0:
        raise RuntimeError(f"Failed to execute command '{dcgmi_cmd}': {out}")
    ci_str = f"CI {gpu_id}/{gi_id}/{ci_id}"
    pattern = rf"\|\s*-> {re.escape(ci_str)}\s*\|\s*Compute Instance \(EntityID: (\d+)\)"
    match = re.search(pattern, out)
    if match:
        return int(match.group(1))
    else:
        raise ValueError(f"Compute Instance {ci_str} not found in the output of '{dcgmi_cmd}' command.")


def _decode_return_values(field_values, field_ids, entity_group_id, entity_id):
    """ Decode the return values from the field group samples. """
    decoded_values = []
    readings = field_values.values[entity_group_id][entity_id]
    for fieldId in field_ids:
        decoded_values.append(readings[fieldId][0].value)
    return decoded_values


def _monitor_resource(
    output_path, stop_event,
    entity_id, entity_group_id,
    group_name, field_group_name,
    update_freq=1,
):
    opMode = dcgm_structs.DCGM_OPERATION_MODE_AUTO
    dcgmHandle = pydcgm.DcgmHandle(ipAddress="localhost", opMode=opMode)
    dcgmSystem = dcgmHandle.GetSystem()
    dcgmGroup = pydcgm.DcgmGroup(dcgmHandle, groupName=group_name)
    dcgmGroup.AddEntity(entity_group_id, entity_id)
    print(f"{group_name} - Monitoring Group ID: {dcgmGroup.GetId()}, included entity: {dcgmGroup.GetEntities()[0]}")
    # Write header only once at the beginning
    pd.DataFrame(columns=CSV_HEADER).to_csv(output_path, index=False)
    field_group = pydcgm.DcgmFieldGroup(
        dcgmHandle,
        name=field_group_name,
        fieldIds=REGISTER_FIELD_IDS
    )
    dcgmSystem.UpdateAllFields(waitForUpdate=True)
    dcgmGroup.samples.WatchFields(
        fieldGroup=field_group,
        updateFreq=int(update_freq * 1e6),
        maxKeepAge=3600,
        maxKeepSamples=3600
    )
    # Open file once, write in append mode
    with open(output_path, 'a') as f:
        while not stop_event.is_set():
            field_values = dcgmGroup.samples.GetLatest_v2(fieldGroup=field_group)
            decoded_values = _decode_return_values(
                field_values,
                field_ids=REGISTER_FIELD_IDS,
                entity_group_id=entity_group_id,
                entity_id=entity_id
            )
            # Write a single line in CSV format
            f.write(','.join(str(v) for v in decoded_values) + '\n')
            f.flush()  # Make sure data is written promptly
            time.sleep(update_freq)


def dcgm_monitor_mig_resource(
    output_path, stop_event,
    gpu_id, gi_id, ci_id,
    update_freq=1
):
    """
    Monitor MIG resource using DCGM. Saves data to output_path as CSV.
    """
    gpu_id = int(gpu_id)
    gi_id = int(gi_id)
    ci_id = int(ci_id)
    entity_id = _getEntityId(gpu_id, gi_id, ci_id)
    entity_group_id = dcgm_fields.DCGM_FE_GPU_CI
    _monitor_resource(
        output_path, stop_event,
        entity_id, entity_group_id,
        group_name="mig_monitoring_group",
        field_group_name="mig_instance_field_group",
        update_freq=update_freq
    )


def dcgm_monitor_gpu_resource(
    output_path, stop_event,
    gpu_id,
    update_freq=1
):
    """
    Monitor GPU resource using DCGM. Saves data to output_path as CSV.
    """
    entity_id = int(gpu_id)
    entity_group_id = dcgm_fields.DCGM_FE_GPU
    _monitor_resource(
        output_path, stop_event,
        entity_id, entity_group_id,
        group_name="gpu_monitoring_group",
        field_group_name="gpu_field_group",
        update_freq=update_freq
    )
