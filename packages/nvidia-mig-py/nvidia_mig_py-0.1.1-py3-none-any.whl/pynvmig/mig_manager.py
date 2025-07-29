import re
import os
import json
from .cmd_util import exec_cmd

__all__ = ["MIGConfigManager"]


class MIGConfigManager:
    """A class to manage MIG configuration and persistence mode on GPUs"""
    # regex patterns
    _GPU_UUID_PATTERN = r'GPU-[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
    _MIG_UUID_PATTERN = r'MIG-[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'

    # gpu_id, mig_profile, mig_uuid = match
    _NVSMI_LIST_PATTERN = r"GPU (\d+):.*?\n\s+MIG (\d+g\.\d+gb).*?\(UUID: (MIG-[a-f0-9-]+)\)"

    # mig_profile, device_id, mig_uuid = match
    _NVSMI_LIST_MIG_UUID_PATTERN = r"MIG\s+([\w\.]+)\s+Device\s+(\d+):\s+\(UUID:\s+(MIG-[a-f0-9-]+)\)"

    # mig_device_id, mig_uuid = match
    _MIG_SEARCH_PATTERN = r"Device  (\d+).*?UUID: (\S+)[^\)]"

    # gpu_id, mig_profile, mig_profile_id, gpu_instance_id = match
    _LGI_PATTERN = r'\|\s+(\d+)\s+MIG\s+([\w\.]+)\s+(\d+)\s+(\d+)\s+'

    # gpu_id, mig_profile, mig_profile_id = match
    _LGIP_PATTERN = r'\s+(\d+)\s+MIG (\d+g\.\d+gb(?:\+\w{2})?)\s+(\d+)'

    # gpu_id, ci_id, mig_profile, gi_id = match
    _LCI_PATTERN = r'\|\s+(\d+)\s+(\d+)\s+MIG\s+([\w\.]+)\s+\d+\s+(\d+)\s+'

    # gpu_instance_id, gpu_id, mig_profile, mig_id = match
    _CGI_PATTERN = r'Successfully created GPU instance ID\s+(\d+)\s+on GPU\s+(\d+)\s+using profile MIG\s+(\d+g.\d+gb)\s+\(ID\s+(\d+)\)'

    # ci_id, gpu_id, gi_id, mig_profile = match
    _CCI_PATTERN = r'Successfully created compute instance ID\s+(\d+)\s+on GPU\s+(\d+)\s+GPU instance ID\s+(\d+)\s+using profile MIG\s+(\S+) \(ID\s+\d+\)'

    # regex for not support
    _NOT_SUPPORT_PATTERN = r'\bNot\s+Supported\b'

    # regex for disabled
    _DISABLED_PATTERN = r'\bDisabled\b'

    def __init__(self) -> None:
        # get GPU information
        self._gpu_list = {}
        self._mig_profile = {}
        self.cur_dir = os.path.dirname(os.path.abspath(__file__))
        self._gpu_profile_json = self.cur_dir + '/mig_profile.json'

        nvsmi_cmd = f'nvidia-smi'
        exit_status, out = exec_cmd(nvsmi_cmd)
        if exit_status != 0:
            raise RuntimeError(f"Failed to execute nvidia-smi command: {out}")

        # check if MIG is disabled
        if re.search(self._DISABLED_PATTERN, out):
            raise Exception("MIG mode is disabled on the system. Please use enable_mig_mode() to enable.")

        list_gpu_cmd = f'sudo nvidia-smi -L'
        exit_status, out = exec_cmd(list_gpu_cmd)
        if exit_status == 0:
            uuid_list = re.findall(self._GPU_UUID_PATTERN, out)
            for index, uuid in enumerate(uuid_list):
                self._gpu_list[index] = uuid
        else:
            raise Exception("Failed to get GPU information")

        # init the MIG profile from the json file if it exists
        if os.path.exists(self._gpu_profile_json):
            with open(self._gpu_profile_json, 'r') as f:
                self._mig_profile = json.load(f)
        else:
            self._profile_mig_config()
            print("MIG profile created.")
            print(json.dumps(self._mig_profile, indent=2))

    def check_gpu_capability(self) -> bool:
        """check if GPU supports MIG mode

        Returns:
            bool: True if GPU supports MIG mode, raise exception otherwise.
        """
        enable_mig_cmd = f"sudo nvidia-smi -mig 1"  # enable MIG mode on all GPUs
        _, out = exec_cmd(enable_mig_cmd)
        if re.search(self._NOT_SUPPORT_PATTERN, out):
            raise Exception("MIG mode is not supported on any GPU")
        return True

    def _profile_mig_config(self):
        """Get MIG profile information and save it to a json file

        Raises:
            Exception: If MIG mode is not enabled on any GPU.
        """
        # check if MIG profile is already loaded
        if self._mig_profile:
            print("MIG profile already loaded from file")
            return

        lgip_cmd = f'sudo nvidia-smi mig -lgip'
        exit_status, out = exec_cmd(lgip_cmd)
        if exit_status == 0:
            matches = re.findall(self._LGIP_PATTERN, out)

            for gpu_id in [str(item[0]) for item in matches]:
                self._mig_profile[f"gpu-{gpu_id}"] = {}
            for match in matches:
                gpu_id, mig_profile, mig_profile_id = match
                self._mig_profile[f"gpu-{gpu_id}"][int(mig_profile_id)] = mig_profile

            with open(self._gpu_profile_json, 'w') as f:
                json.dump(self._mig_profile, f, indent=2)
        elif exit_status == 6:
            raise Exception(out)

    def get_mig_profile(self, gpu_id: int = None) -> dict:
        """Get MIG profile information for a specific GPU or all GPUs

        Args:
            gpu_id (int, optional): The GPU ID to get the MIG profile for. If None, get the MIG profile for all GPUs.

        Returns:
            dict: A dictionary containing the MIG profile information.
            Example:
            {'gpu-0': {'14': '1g.6gb',
                    '21': '1g.6gb+me',
                    '5': '2g.12gb',
                    '6': '2g.12gb+me',
                    '0': '4g.24gb'},
            'gpu-1': {'14': '1g.6gb',
                    '21': '1g.6gb+me',
                    '5': '2g.12gb',
                    '6': '2g.12gb+me',
                    '0': '4g.24gb'},
            'gpu-2': {'14': '1g.6gb',
                    '21': '1g.6gb+me',
                    '5': '2g.12gb',
                    '6': '2g.12gb+me',
                    '0': '4g.24gb'},
            'gpu-3': {'14': '1g.6gb',
                    '21': '1g.6gb+me',
                    '5': '2g.12gb',
                    '6': '2g.12gb+me',
                    '0': '4g.24gb'}}
        """
        if gpu_id is not None:
            if f"gpu-{gpu_id}" not in self._mig_profile:
                raise Exception(f"GPU {gpu_id} does not support MIG mode")
            return self._mig_profile[f"gpu-{gpu_id}"]
        else:
            return self._mig_profile

    def get_smallest_mig_profile(self, gpu_id: int = None) -> str:
        """Get the smallest MIG profile for a specific GPU
        Args:
            gpu_id (int, optional): The GPU ID to get the smallest MIG profile for. If None, get the smallest MIG profile for all GPUs.

        Returns:
            str: The smallest MIG profile.
        """
        if gpu_id is None:
            raise Exception("GPU ID is required to get the smallest MIG profile")
        mig_profile = self.get_mig_profile(gpu_id)
        if not mig_profile:
            raise Exception("No MIG profiles found")

        def extract_gb(profile_str):
            # Ignore profiles with '+me'
            if '+me' in profile_str:
                return float('inf')
            # Extract the smallest profile by GB, e.g., '1g.6gb' -> 6
            match = re.search(r'(\d+)gb', profile_str)
            return int(match.group(1)) if match else float('inf')

        # Find the key (profile_id) and value (profile_str) of the smallest profile
        min_profile_id, min_profile_str = min(
            ((profile_id, profile_str) for profile_id, profile_str in mig_profile.items()),
            key=lambda item: extract_gb(item[1])
        )
        return min_profile_id, min_profile_str

    def enable_mig_mode(self, gpu_id: int or list[int] = None):  # type: ignore
        # TODO needs validate MIG model is in pending
        """Enable MIG mode on GPUs

        Args:
            gpu_id (int or list, optional): The GPU ID(s) to enable MIG configuration on. If None, enable on all GPUs.

        """
        if isinstance(gpu_id, list):
            if max(gpu_id) >= len(self._gpu_list) or min(gpu_id) < 0:
                raise Exception("Invalid GPU ID")
            else:
                gpu_id = ','.join([str(i) for i in gpu_id])

        enable_mig_cmd = f"sudo nvidia-smi -mig 1"  # enable MIG mode on all GPUs

        if gpu_id is not None:
            enable_mig_cmd += f" -i {gpu_id}"  # enable MIG mode on a specific GPU
        exit_status, out = exec_cmd(enable_mig_cmd)
        if exit_status == 0:
            print(out, end='')
            print("MIG mode enabled successfully")
            self._profile_mig_config()
        else:
            print(exit_status)
            print(out, end='')
            raise Exception("Failed to enable MIG mode")

    def disable_mig_mode(self, gpu_id: int or list[int] = None):  # type: ignore
        """Disable MIG mode on GPUs

        Args:
            gpu_id (list, optional): The GPU IDs to disable MIG configuration on. If None, disable on all GPUs.

        """
        if isinstance(gpu_id, list):
            if max(gpu_id) >= len(self._gpu_list) or min(gpu_id) < 0:
                raise Exception("Invalid GPU ID")
            else:
                gpu_id = ','.join([str(i) for i in gpu_id])

        disable_mig_cmd = f"sudo nvidia-smi -mig 0"  # disable MIG mode on all GPUs

        if gpu_id is not None:
            disable_mig_cmd += f" -i {gpu_id}"  # disable MIG mode on a specific GPU
        exit_status, out = exec_cmd(disable_mig_cmd)
        if exit_status == 0:
            print(out, end='')
            print("MIG mode disabled successfully")
        else:
            print(exit_status)
            print(out, end='')
            raise Exception("Failed to disable MIG mode")

    def enable_pm_mode(self, gpu_id: int or list[int] = None):  # type: ignore
        """Enable persistence mode on GPUs

        Args:
            gpu_id (list, optional): The GPU IDs to enable persistence mode on. If None, enable on all GPUs. Defaults to None.
        """
        if isinstance(gpu_id, list):
            if max(gpu_id) >= len(self._gpu_list) or min(gpu_id) < 0:
                raise Exception("Invalid GPU ID")
            else:
                gpu_id = ','.join([str(i) for i in gpu_id])

        enable_pm_cmd = f'sudo nvidia-smi -pm 1'  # enable persistence mode on all GPUs

        if gpu_id is not None:
            enable_pm_cmd += f" -i {gpu_id}"  # enable MIG mode on a specific GPU
        exit_status, out = exec_cmd(enable_pm_cmd)
        if exit_status == 0:
            print(out, end='')
            print("Persistence mode enabled successfully")
        else:
            print(exit_status)
            print(out, end='')
            raise Exception(f"Failed to enable persistence mode")

    def disable_pm_mode(self, gpu_id: int or list[int] = None):  # type: ignore
        """Disable persistence mode on GPUs

        Args:
            gpu_id (int or list, optional): The GPU IDs to disable persistence mode on. If None, disable on all GPUs. Defaults to None.

        """
        if isinstance(gpu_id, list):
            if max(gpu_id) >= len(self._gpu_list) or min(gpu_id) < 0:
                raise Exception("Invalid GPU ID")
            else:
                gpu_id = ','.join([str(i) for i in gpu_id])
        elif gpu_id is not None and not isinstance(gpu_id, int):
            raise TypeError("gpu_id must be an int or a list of ints")
        elif gpu_id not in self._gpu_list:
            raise ValueError(f"Invalid GPU ID {gpu_id}, available GPUs are {list(self._gpu_list.keys())}")

        disable_pm_cmd = f'sudo nvidia-smi -pm 0'  # disable persistence mode on all GPUs

        if gpu_id is not None:
            disable_pm_cmd += f" -i {gpu_id}"  # disable persistence mode on a specific GPU
        exit_status, out = exec_cmd(disable_pm_cmd)
        if exit_status == 0:
            print(out, end='')
            print("Persistence mode disabled successfully")
        else:
            print(exit_status)
            print(out, end='')
            raise Exception("Failed to disable persistence mode")

    # type: ignore
    def create_gpu_instance(self, gpu_id: int, profile_id, create_ci: bool = True) -> list[dict]:
        """Create a GPU instance on given gpu (gpu_id) with a specific MIG profile (profile_id)

        Args:
            gpu_id (int): The GPU ID to create the GPU instance on.
            profile_id (int or list[int]): The MIG profile ID to create the GPU instance with.
            create_ci (bool, optional): Whether to create a compute instance on the GPU instance. Default to False.
        Returns:
            list[dict]: If create_ci is True, return a list of MIG UUIDs of the created compute instance, else return a list of created MIG IDs on given GPU.
        """
        # TODO separate status checking from the actual operation

        # load MIG profile from file
        try:
            with open(self._gpu_profile_json, 'r') as f:
                self._mig_profile = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                "MIG profile file not found, please run _profile_mig_config() first"
            )

        if gpu_id not in self._gpu_list:
            raise ValueError(f"Invalid GPU ID {gpu_id}, available GPUs are {list(self._gpu_list.keys())}")

        # get valid instance IDs for given GPU
        valid_profile_ids = [int(item) for item in self._mig_profile[f'gpu-{gpu_id}'].keys()]

        prompt_str_suffix = ''
        if isinstance(profile_id, int):
            if profile_id not in valid_profile_ids:
                # if gi_id is not valid
                raise ValueError(
                    f"Invalid MIG profile ID {profile_id} for GPU {gpu_id}, available MIG profiles are {valid_profile_ids}"
                )

            # formulate the prompt suffix for gi_id
            prompt_str_suffix += f'{profile_id}:{self._mig_profile[f"gpu-{gpu_id}"][f"{profile_id}"]}'

        if isinstance(profile_id, list):
            for idx, id in enumerate(profile_id):
                if id not in valid_profile_ids:
                    # if gi_id is not valid
                    raise ValueError(
                        f"Invalid MIG profile ID {id} for GPU {gpu_id}, available MIG profiles are {valid_profile_ids}"
                    )

                # formulate the prompt suffix for gi_id
                if idx < len(profile_id) - 1:
                    prompt_str_suffix += f'{id}:{self._mig_profile[f"gpu-{gpu_id}"][f"{id}"]}, '
                else:
                    prompt_str_suffix += f'{id}:{self._mig_profile[f"gpu-{gpu_id}"][f"{id}"]}.'

            # if gi_id is a list, join the IDs with comma to formulate the final command
            profile_id = ','.join([str(i) for i in profile_id])

        cgi_cmd = f'sudo nvidia-smi mig -i {gpu_id} -cgi {profile_id}'

        prompt = f"Successfully created GPU instance on GPU {gpu_id} with MIG profile {prompt_str_suffix}"
        if create_ci:
            # cmd to create the default compute instance on the MIG instances
            cgi_cmd += f' -C'
            prompt += " and created compute instance on GPU instance."

        exit_status, cgi_cmd_out = exec_cmd(cgi_cmd)
        # if the command fails, raise an exception
        if 'Failed' in cgi_cmd_out or 'No' in cgi_cmd_out or exit_status != 0:
            raise RuntimeError(f'Failed executing command: {cgi_cmd}\n{cgi_cmd_out}')

        # print the output prompt
        print(prompt)

        if create_ci:
            return self.list_compute_instances(gpu_id)
        else:
            return self.list_gpu_instances(gpu_id)

    def list_gpu_instances(self, gpu_id: int = None) -> list[dict]:
        """List all GPU instances on given GPU.
        If gpu_id is not specified, list GPU instances on all GPUs.

        Args:
            gpu_id (int, optional): GPU ID. Defaults to None.

        Returns:
            list[dict]: A list of dictionaries containing GPU instance information.
        """
        lci_cmd = f'sudo nvidia-smi mig -lgi'
        if gpu_id is not None:
            lci_cmd += f' -i {gpu_id}'

        exit_status, lci_out = exec_cmd(lci_cmd)

        gi_list = []
        if exit_status != 0:
            raise Exception(f"Failed to list compute instances on GPU-{gpu_id}. {lci_out}")
        else:
            matches = re.findall(self._LGI_PATTERN, lci_out)
            for match in matches:
                gpu_id, mig_profile, profile_id, gi_id = match
                gi_list.append({
                    "gpu_id": gpu_id,
                    "gi_id": gi_id,
                    "mig_profile": mig_profile
                })
        return gi_list

    def create_compute_instance(self, gpu_id: int = None, gi_id: int or list[int] = None) -> list[str]:  # type: ignore
        """Create a compute instance on given MIG device id(s) on given GPU. 
        If gpu_id and gi_id are not specified, create a compute instance on all MIG devices on all GPUs.

        Args:
            gpu_id (int): The GPU ID of the MIG device to create the compute instance on.
            gi_id (int or list[int]): The MIG device ID(s) to create the compute instance on.

        Returns:
            list[str]: A list of MIG device(s) UUID(s) of the created compute instance.
        """
        # TODO only return true or false of whether the operation is successful
        cci_cmd = f'sudo nvidia-smi mig -cci'
        if gpu_id is not None:
            cci_cmd += f' -i {gpu_id}'
        if gi_id is not None:
            if isinstance(gi_id, list):
                gi_id = ','.join([str(i) for i in gi_id])
            cci_cmd += f' -gi {gi_id}'

        exit_status, cci_out = exec_cmd(cci_cmd)
        if exit_status == 0:
            print(cci_out, end='')
            return self.list_compute_instances(gpu_id)
        else:
            raise Exception(f"Creating compute instances failed on GPU-{gpu_id}: {cci_out}")

    def list_compute_instances(self, gpu_id: int = None) -> list[dict]:
        """List all compute instances on given GPU.
        If gpu_id is not specified, list compute instances on all GPUs.

        Args:
            gpu_id (int, optional): GPU ID. Defaults to None.

        Returns:
            list[dict]: A list of dictionaries containing compute instance information.
            Example:
            [{
                "gpu_id": gpu_id,
                "gi_id": gi_id,
                "ci_id": ci_id,
                "mig_profile": mig_profile
            }]
        """

        lci_cmd = f'sudo nvidia-smi mig -lci'
        if gpu_id is not None:
            lci_cmd += f' -i {gpu_id}'

        exit_status, lci_out = exec_cmd(lci_cmd)

        ci_list = []
        if exit_status != 0:
            raise RuntimeError(f"Failed to list compute instances on GPU-{gpu_id}. {lci_out}")
        else:
            matches = re.findall(self._LCI_PATTERN, lci_out)
            for match in matches:
                gpu_id, gi_id, mig_profile, ci_id = match
                # gpu_uuid = self._gpu_list.get(int(gpu_id))
                # ci_uuid = f"MIG-{gpu_uuid}/{gi_id}/{ci_id}"
                ci_list.append({
                    "gpu_id": gpu_id,
                    "gi_id": gi_id,
                    "ci_id": ci_id,
                    # "CI_uuid": ci_uuid,
                    "mig_profile": mig_profile
                })
        return ci_list

    def destroy_compute_instance(self, gpu_id: int = None, gi_id=None) -> list[str]:
        """Destroy all compute instances on given MIG GPU instance id on given GPU. 
        If gpu_id and gi_id are not specified, destroy compute instances on all MIG devices on all GPUs.

        Args:
            gpu_id (int): The GPU ID of the MIG device to destroy the compute instance on.
            profile_id (int or list[int]): The MIG profile_id.

        Returns:            
            list[str]: A list of MIG device(s) UUID(s) of the destroyed compute instance.
        """
        dci_cmd = f'sudo nvidia-smi mig -dci'
        if gpu_id is not None:
            dci_cmd += f' -i {gpu_id}'

        if gi_id is not None:
            if isinstance(gi_id, list):
                gi_id_valid = []
                for gi_id_item in gi_id:
                    try:
                        self.list_compute_instances(gpu_id)  # validate gi_id
                        gi_id_valid.append(gi_id_item)
                    except Exception:
                        pass
                gi_id = ','.join([str(i) for i in gi_id_valid])
            dci_cmd += f' -gi {gi_id}'

        exit_status, dci_out = exec_cmd(dci_cmd)
        if exit_status == 0:
            print(dci_out, end='')
        else:
            raise Exception(f"Failed destroying compute instances on GPU instance {gi_id}: {dci_out}")

    def destroy_gpu_instance(self, gpu_id: int = None, gi_id: int or list[int] = None) -> list[str]:  # type: ignore
        """Destroy a GPU instance on given GPU with a specific MIG profile. 
        If gpu_id and gi_id are not specified, destroy GPU instances on all GPUs with all MIG profiles.

        Args:
            gpu_id (int): The GPU ID to destroy the GPU instance on.
            gi_id (int or list[int]): The MIG profile ID to destroy the GPU instance with.

        Returns:
            list[str]: A list of MIG UUIDs of the destroyed GPU instance.
        """
        try:
            self.destroy_compute_instance(gpu_id, gi_id)  # destroy compute instance first
        except:
            pass

        dgi_cmd = f'sudo nvidia-smi mig -dgi'
        if gpu_id is not None:
            dgi_cmd += f' -i {gpu_id}'
        if gi_id is not None:
            if isinstance(gi_id, list):
                gi_id = ','.join([str(i) for i in gi_id])
            dgi_cmd += f' -gi {gi_id}'

        exit_status, dgi_out = exec_cmd(dgi_cmd)
        if exit_status == 0:
            print(dgi_out, end='')
        else:
            print("Destroying GPU instances failed.", dgi_out, end='')

    def get_mig_devices_uuids(self, gpu_id: int = None) -> list[str]:
        """Get the UUIDs of all MIG devices on a specific GPU or all GPUs

        Args:
            gpu_id (int, optional): GPU ID. Defaults to None.

        Returns:
            list[str]: A list of MIG device UUIDs.
            Example:
            [{
                "gpu_id": gid,
                "dev_id": device_id,
                "uuid": mig_uuid,
                "mig_profile": mig_profile
            }]
        """
        query_cmd = f'nvidia-smi -L'
        exit_status, query_out = exec_cmd(query_cmd)

        if exit_status != 0:
            raise Exception(f"Failed to query MIG devices: {query_out}")

        return_list = []
        gpu_ids = self._gpu_list.keys() if gpu_id is None else [gpu_id]
        for gid in gpu_ids:
            pattern = rf"GPU {gid}:.*?(?=^GPU \d+:|\Z)"
            gpu_block = re.search(pattern, query_out, re.DOTALL | re.MULTILINE)
            if gpu_block:
                migs = re.findall(self._NVSMI_LIST_MIG_UUID_PATTERN, gpu_block.group())
                for mig_profile, device_id, uuid in migs:
                    return_list.append({
                        "gpu_id": gid,
                        "dev_id": device_id,
                        "uuid": uuid,
                        "mig_profile": mig_profile
                    })
        return return_list


if __name__ == '__main__':
    mig_config_manager = MIGConfigManager()

    mig_config_manager.enable_pm_mode()
    mig_config_manager.enable_mig_mode()
    mig_config_manager._profile_mig_config()
    gpu_0_list = mig_config_manager.create_gpu_instance(0, [0], 1)
    gpu_1_list = mig_config_manager.create_gpu_instance(1, [0], 1)
    gpu_2_list = mig_config_manager.create_gpu_instance(2, [0], 1)
    gpu_3_list = mig_config_manager.create_gpu_instance(3, [0], 1)
    # gpu_0_list = mig_config_manager.create_gpu_instance(1, [14, 14, 14, 14], 1)
    # gpu_0_list = mig_config_manager.create_gpu_instance(2, [14, 14, 14, 14], 1)
    # gpu_0_list = mig_config_manager.create_gpu_instance(3, [14, 14, 14, 14], 1)
    # print(gpu_0_list)
    # gpu_1_list = mig_config_manager.create_gpu_instance(1, [0], 1)
    # print(gpu_1_list)
    # gpu_2_list = mig_config_manager.create_gpu_instance(2, [14, 14, 5], 0)
    # print(gpu_2_list)
    # gpu_3_list = mig_config_manager.create_gpu_instance(3, [5, 5], 0)
    # print(gpu_3_list)
    # print(get_gpu_device_uuid(0, 2))
    # mig_config_manager.create_compute_instance(2, [2, 3, 4])
    # gpu_1_list = mig_config_manager.create_gpu_instance(0, [14, 5, 14], False)
    # pprint.pprint(gpu_1_list)
    # gpu_2_list = mig_config_manager.create_gpu_instance(2, [0], False)
    # pprint.pprint(gpu_2_list)
    # mig_config_manager.destroy_compute_instance()
    # mig_config_manager.destroy_gpu_instance()
    # mig_config_manager.disable_mig_mode()
    # mig_config_manager.disable_pm_mode()
