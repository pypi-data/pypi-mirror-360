def get_formatted_volume_list_and_total_size(list_of_volumes: list):
    """Method format data in list of volumes to be displayed in table and calculate total size of volumes

    :param list_of_volumes: list of volumes to be formatted
    :type list_of_volumes: list
    :return: list of volumes to be displayed in table and total size of volumes
    :rtype: list, int
    """
    list_to_print = []
    total_size = 0
    for volume in list_of_volumes:
        name = volume["name"]
        used = volume["used"]
        size = volume["size"]
        disks_type = volume["disks_type"]
        access_types = ", ".join(volume["access_types"])
        mounts = volume["mounted_to"]
        mounts[:] = [s.rsplit("-", 2)[0] for s in mounts]
        all_mounted_to = ", ".join(mounts)
        total_size += int("".join(filter(str.isdigit, size)))
        row_list = [name, used, size, access_types, disks_type, all_mounted_to]
        list_to_print.append(row_list)
    return list_to_print, total_size


def convert_node_resource_value_from_string(
    value: str, resource_type: str = None
) -> int:
    """Units Converter.
    For CPU it returns in "m".
    For storage it returns in "Mb".
    For memory it can return in "m".

    :param value: value
    :type value: str
    :return: converted value
    :rtype: int
    """
    if value.endswith("Ti"):
        return int("".join(filter(str.isdigit, value))) * 1000 * 1000
    elif value.endswith("Mb"):
        return int("".join(filter(str.isdigit, value)))
    elif value.endswith("m"):
        if resource_type is not None:
            # 1 cpu = 1000m cpu
            if (
                resource_type.split(".")[-1].lower() == "memory"
            ):  #  requests.memory: 1 932 735 283 200m ~= 2Gi
                return int(int("".join(filter(str.isdigit, value))) / 10**9)
        return int("".join(filter(str.isdigit, value)))
    else:  # ex. Gi
        return int("".join(filter(str.isdigit, value))) * 1000
