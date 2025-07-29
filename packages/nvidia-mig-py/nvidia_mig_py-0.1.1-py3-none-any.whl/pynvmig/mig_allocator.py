import re
from collections import defaultdict
from .mig_manager import MIGConfigManager
from .cmd_util import exec_cmd

__all__ = ["MIGInstanceAllocator"]


class MIGInstanceAllocator:
    """
    Class to manage and allocate MIG instances based on memory requirements.
    """

    # match = gpu_id, gi_id, ci_id, dev_id
    _NVSMI_MIG_DEV_PATTERN = r"\|\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\|"

    # match = gpu_id, gi_id, ci_id, pid, proc_name, mem_usage
    _NVSMI_MIG_PID_PATTERN = r"\|\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\w+\s+([^\s]+)\s+(\d+)MiB\s*\|"

    def __init__(self):

        self._mcg = MIGConfigManager()
        self._mig_profile = self._mcg.get_mig_profile()
        # gpu_id, gi_id, ci_id, dev_id, uuid, mig_profile, pid, p_name, mem_usage, allocated
        self._mig_resource_list = []
        self.init_mig_resources()

    def init_mig_resources(self):
        try:
            self._update_mig_resource_status()
        except Exception:
            self._reinitialize_mig_resources()
            print(f"Finished reinitializing MIG resources.")
            self._update_mig_resource_status()

        gpu_ids_to_be_reset = self._are_idle_mig_instances_smallest()
        if not gpu_ids_to_be_reset:
            return
        self._reinitialize_mig_resources(gpu_ids_to_be_reset)
        print(f"Finished reinitializing MIG resources.")
        # Reinitialize the MIG resource list after resetting the MIG instances
        self._update_mig_resource_status()

    def get_mig_resource_list(self):
        """
        Get the list of MIG resources with their details.

        Returns:
            list: List of dictionaries containing MIG resource information.
        """
        return self._mig_resource_list

    def get_mig_resource_by_pid(self, pid: int):
        """
        Get MIG resource information by process ID (PID).

        Args:
            pid (int): Process ID to search for.
        Returns:
            dict: MIG resource information associated with the given PID.
        Raises:
            ValueError: If no MIG resource is found with the specified PID.
        """
        for mig_resource in self._mig_resource_list:
            if mig_resource["pid"] == str(pid):
                return mig_resource
        raise ValueError(f"No MIG resource found with PID {pid}.")

    def allocate_mig_resource(self, required_mem: int, gpu_id: int = None):
        """ Allocate a MIG resource based on the required memory.

        Args:
            required_mem (int): Required memory in GB.
            gpu_id (int, optional): GPU ID to allocate the MIG instance on. If None, try to allocate on the first available GPU.
        """
        try:
            mig_resource = self.get_mig_resource_by_memory(required_mem, gpu_id)
        except ValueError as e:
            # try to create a new MIG instance if no suitable resource is found
            if not self.create_gpu_instance_by_memory(required_mem, gpu_id):
                raise ValueError(
                    f"Failed to allocate MIG resource with {required_mem}GB memory. "
                    f"Please ensure that the required memory is available or create a new MIG instance."
                )
            mig_resource = self.get_mig_resource_by_memory(required_mem, gpu_id)

        # set the allocated flag to True
        mig_resource["allocated"] = True

        # temporarily set the PID to -1 to indicate that the resource is being allocated
        mig_resource["pid"] = -1
        return mig_resource

    def get_mig_resource_by_memory(self, required_mem: int, gpu_id: int = None):
        """
        Get MIG compute instance UUIDs based on required memory.

        Args:
            required_mem (int): Required memory in GB.
        Returns:
            dict: MIG resource information with sufficient memory.
            Example:
            {
                "gpu_id": gpu_id,
                "gi_id": gi_id,
                "ci_id": ci_id,
                "dev_id": dev_id,
                "uuid": uuid,
                "mig_profile": mig_profile,
                "pid": None,
                "p_name": None,
                "mem_usage": None,
                "allocated": False
            }
        Raises:
            ValueError: If no available MIG compute instance is found with the required memory.
        """

        if self._all_instances_busy():
            raise RuntimeError("Cannot allocate a new MIG instance, all instances are busy.")

        if required_mem <= 0:
            raise ValueError("Required memory must be greater than 0.")

        if gpu_id is not None and self._all_instances_busy_by_gpu(gpu_id):
            raise RuntimeError(f"Cannot allocate a new MIG instance on GPU {gpu_id}, all instances are busy.")

        # Filter resources without PID and (if specified) matching gpu_id
        filtered_resources = []
        for mig_instance_resource in self._mig_resource_list:
            if mig_instance_resource["allocated"] is False:  # Check if the resource is not allocated
                if gpu_id is None or mig_instance_resource["gpu_id"] == gpu_id:
                    filtered_resources.append(mig_instance_resource)

        # Build a list of (mem_size, resource) tuples
        mem_resource_pairs = defaultdict(list)
        for mig_instance_resource in filtered_resources:
            mig_profile: str = mig_instance_resource["mig_profile"]
            mem_size = int(mig_profile.split('.')[-1].replace('gb', ''))
            mem_resource_pairs[mem_size].append(mig_instance_resource)

        # Return the first resource with the smallest memory value
        for mem_size in sorted(mem_resource_pairs.keys()):
            if mem_size >= required_mem:
                # Return the first resource with this memory size
                return mem_resource_pairs[mem_size][0]
        raise ValueError(
            f"No available MIG compute instance found with at least {required_mem}GB memory, please use `create_gpu_instance_by_memory()` to create a MIG compute instance with the required memory."
        )

    def create_gpu_instance_by_memory(self, required_mem: int, gpu_id: int = None):
        """
        Create a MIG compute instance with the specified memory requirement.

        Args:
            required_mem (int): Required memory in GB.
            gpu_id (int, optional): GPU ID to create the MIG instance on. If None, any available GPU will be used.
        Returns:
            dict: Information about the created MIG compute instance.
        """
        if self._all_instances_busy():
            raise RuntimeError("Cannot create a new instance, all MIG instances are busy.")

        # loop through the GPUs to find the smallest MIG profile that meets the memory requirement
        for gpu_label, profiles in self._mig_profile.items():

            gpu_index = int(gpu_label.split('-')[-1])

            if gpu_id is not None and gpu_index != gpu_id:
                # Skip GPUs that do not match the specified gpu_id if gpu_id is provided
                continue

            if self._all_instances_busy_by_gpu(gpu_index):
                print(f"All MIG instances on GPU {gpu_index} are busy, skipping.")
                continue

            # Filter profiles without '+me' and with sufficient memory
            filtered_profile = {
                k: int(v.split('.')[-1].replace('gb', ''))
                for k, v in profiles.items() if '+me' not in v
            }

            # Find the profile with smallest memory >= required
            valid_profiles = {
                k: mem for k, mem in filtered_profile.items() if mem >= required_mem
            }

            if not valid_profiles:
                print(f"No suitable MIG profile on GPU {gpu_index} with at least {required_mem}GB memory.")
                continue

            # Find the profile key with the smallest memory >= required_mem
            best_profile_key = min(valid_profiles, key=valid_profiles.get)
            selected_profile = profiles[best_profile_key]

            # TODO dynamically create the MIG instance
            # find all free 6gb instances from the mig_resource_list on the same GPU
            free_instances = [
                resource for resource in self._mig_resource_list
                if resource["pid"] is None and resource["gpu_id"] == gpu_index and
                resource["mig_profile"] == "1g.6gb"
            ]

            # if best_profile_key is 5, which means we need to create a 12GB instance
            if best_profile_key == "5" and len(free_instances) < 2:
                print(f"Not enough free 6GB instances on GPU {gpu_index} to create a 12GB instance.")
                continue
            elif best_profile_key == "0" and len(free_instances) < 4:
                print(f"Not enough free 6GB instances on GPU {gpu_index} to create a 24GB instance.")
                continue

            print(
                f"Creating MIG instance {selected_profile} on GPU {gpu_index} with profile {best_profile_key} for {required_mem}GB memory instance."
            )

            # destroy the free_instances first
            # resource has keys: gpu_id, gi_id, ci_id, dev_id, uuid, mig_profile, pid, p_name, mem_usage
            # Only destroy the required number of instances based on the profile key
            if best_profile_key == "5":
                # For 2g.12gb, destroy only the last two free 6GB instances
                for resource in free_instances[-2:]:
                    self._mcg.destroy_gpu_instance(
                        resource["gpu_id"],
                        resource["gi_id"]
                    )
            else:
                # For 4g.24gb, destroy all free 6GB instances
                for resource in free_instances:
                    self._mcg.destroy_gpu_instance(
                        resource["gpu_id"],
                        resource["gi_id"]
                    )

            # create the MIG instance with the selected profile
            try:
                self._mcg.create_gpu_instance(gpu_index, int(best_profile_key), True)
            except RuntimeError as e:
                print(f"Failed to create MIG instance on GPU {gpu_index}: {e}")
                continue

            # Reinitialize the MIG resource list after creating the instance
            self._update_mig_resource_status()
            return True

        raise ValueError(
            f"Insufficient free memory to create a MIG instance with {required_mem}GB "
            f"{f'on GPU {gpu_id}' if gpu_id is not None else 'on any available GPU'}. "
            f"Consider requesting a smaller memory size or freeing up existing instances."
        )

    def _reinitialize_mig_resources(self, gpu_ids_to_be_reset=[]):
        """ Reinitialize MIG resources by destroying idle instances and creating the smallest MIG instance.

        Args:
            gpu_ids_to_be_reset (list, optional): _description_. Defaults to [].
        """

        if not gpu_ids_to_be_reset:
            gpu_ids_to_be_reset = [i for i in range(len(self._mig_profile))]

        print("Reinitializing MIG resources on GPUs:", gpu_ids_to_be_reset)
        # Destroy all idle MIG resources for the GPUs that need to be reset
        for resource in self._mig_resource_list:
            if resource["pid"] is not None:
                continue
            gpu_id = resource["gpu_id"]
            if gpu_id not in gpu_ids_to_be_reset:
                continue
            gi_id = resource["gi_id"]
            self._mcg.destroy_gpu_instance(gpu_id, gi_id)

        # loop through the MIG profiles and create the smallest MIG instance
        for gpu_label, profiles in self._mig_profile.items():
            # gpu_label: "gpu-0"
            gpu_index = int(gpu_label.split('-')[-1])
            if gpu_index not in gpu_ids_to_be_reset:
                continue
            # profiles: {'14': '1g.6gb','21': '1g.6gb+me','5': '2g.12gb','6': '2g.12gb+me','0': '4g.24gb'}
            filtered = {
                k: int(v.split('.')[-1].replace('gb', ''))
                for k, v in profiles.items() if '+me' not in v
            }

            # Extract the key with the smallest memory size
            min_key = int(min(
                filtered,
                key=lambda k: int(filtered[k])
            ))

            # Create the smallest MIG instance for this GPU
            while True:
                try:
                    self._mcg.create_gpu_instance(gpu_index, min_key, True)
                except RuntimeError:
                    print(f"Finished creating partition on GPU {gpu_index}")
                    break

    def _update_mig_resource_status(self):
        """ Update the status of MIG resources by executing `nvidia-smi` command.
        This method retrieves the current status of MIG resources, including GPU IDs, GI IDs,
        CI IDs, device IDs, UUIDs, MIG profiles, and associated process information.

        Raises:
            RuntimeError: If the `nvidia-smi` command fails to execute or returns an error.
        """

        allocated_resources = [
            resource for resource in self._mig_resource_list if resource["allocated"]
        ]
        allocated_mig_uuids = [resource["uuid"] for resource in allocated_resources]

        self._mig_resource_list.clear()
        self._mig_resource_list.extend(allocated_resources)
        ci_list = self._mcg.list_compute_instances()
        uuid_list = self._mcg.get_mig_devices_uuids()

        nvsmi_cmd = "nvidia-smi"
        exit_status, out = exec_cmd(nvsmi_cmd)
        if exit_status != 0:
            raise RuntimeError(f"Failed to execute command '{nvsmi_cmd}': {out}")

        matches = re.findall(self._NVSMI_MIG_DEV_PATTERN, out)
        for match in matches:
            gpu_id, gi_id, ci_id, dev_id = map(int, match)
            # Find the matching compute instance from ci_list
            ci_match = next(
                (
                    ci for ci in ci_list
                    if int(ci["gpu_id"]) == gpu_id and
                    int(ci["gi_id"]) == gi_id and
                    int(ci["ci_id"]) == ci_id
                ), None
            )
            mig_profile = ci_match['mig_profile'] if ci_match else None

            uuid_match = next(
                (
                    mig_uuid for mig_uuid in uuid_list
                    if int(mig_uuid["gpu_id"]) == gpu_id and
                    int(mig_uuid["dev_id"]) == dev_id
                ), None
            )
            uuid = uuid_match['uuid'] if uuid_match else None
            if uuid in allocated_mig_uuids:
                # Skip already allocated MIG resources
                continue
            resource_info = {
                "gpu_id": gpu_id,
                "gi_id": gi_id,
                "ci_id": ci_id,
                "dev_id": dev_id,
                "uuid": uuid,
                "mig_profile": mig_profile,
                "pid": None,
                "p_name": None,
                "mem_usage": None,
                "allocated": False  # Initially set to False
            }
            self._mig_resource_list.append(resource_info)
            self._update_mig_resource_pid(out)

    def _are_idle_mig_instances_smallest(self):
        """ Check if all idle MIG instances are the smallest available for all GPUs.
        Returns:
            list: List of GPU IDs that have idle MIG instances which are not the smallest.
            If all idle MIG instances are the smallest, returns an empty list.
        """
        ret_gpu_ids = []
        for resource in self._mig_resource_list:
            if resource["pid"] is None:
                # If the resource has no PID, check if it is the smallest MIG instance
                gpu_id = resource["gpu_id"]
                gi_id = resource["gi_id"]
                mig_profile = resource["mig_profile"]

                # Get the smallest MIG profile for this GPU
                s_gi_id, smallest_profile = self._mcg.get_smallest_mig_profile(gpu_id)
                if gi_id != s_gi_id and mig_profile != smallest_profile:
                    ret_gpu_ids.append(gpu_id)
        return list(set(ret_gpu_ids))

    def _update_mig_resource_pid(self, nvsmi_output=None):
        """ Update the PID and process name for each MIG resource.
        This method parses the output of the `nvidia-smi` command to find the process IDs and names
        associated with each MIG resource, and updates the resource list accordingly.
        Args:
            nvsmi_output (str, optional): Output of the `nvidia-smi` command. If not provided,
                                          it will execute the command to get the output.
        """
        if nvsmi_output is None:
            nvsmi_cmd = "nvidia-smi"
            exit_status, nvsmi_output = exec_cmd(nvsmi_cmd)
            if exit_status != 0:
                raise RuntimeError(f"Failed to execute command '{nvsmi_cmd}': {nvsmi_output}")
        matches = re.findall(self._NVSMI_MIG_PID_PATTERN, nvsmi_output)
        for match in matches:
            gpu_id, gi_id, ci_id, pid, proc_name, mem_usage = match
            # Convert to integers where necessary
            gpu_id = int(gpu_id)
            gi_id = int(gi_id)
            ci_id = int(ci_id)
            mem_usage = int(mem_usage)

            # Find the matching resource in the resource list
            for resource in self._mig_resource_list:
                if (
                    resource["gpu_id"] == gpu_id and
                    resource["gi_id"] == gi_id and
                    resource["ci_id"] == ci_id
                ):
                    resource["pid"] = pid
                    resource["p_name"] = proc_name
                    resource["mem_usage"] = mem_usage
                    resource["allocated"] = True
                    break

    def _all_instances_busy(self):
        """ Check if all MIG instances are busy (i.e., have a PID).
        Returns:
            bool: True if all MIG instances are busy, False otherwise.
        """
        return all(resource["allocated"] for resource in self._mig_resource_list)

    def _all_instances_busy_by_gpu(self, gpu_id: int):
        """ Check if all MIG instances on a specific GPU are busy.
        Args:
            gpu_id (int): The GPU ID to check.
        Returns:
            bool: True if all MIG instances on the specified GPU are busy, False otherwise.
        """
        return all(
            resource["allocated"] for resource in self._mig_resource_list
            if resource["gpu_id"] == gpu_id
        )
