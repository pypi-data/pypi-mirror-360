def list_get_mounted_volumes(volume_list: list) -> str:
    """Formats and returns list of PVC volumes mounted to an app.

    :param volume_list: list of all volumes mounted to an app
    :type volume_list: list
    :return: list of PVC volumes
    :rtype: str
    """
    volume_name_list = []
    for volume in volume_list:
        volume_type = volume.get("type")
        if volume_type == "PVC":
            volume_name = volume.get("name")
            volume_name_list.append(volume_name)
    volumes_mounted = (
        ", ".join(volume_name_list) if len(volume_name_list) != 0 else None
    )
    return volumes_mounted


def get_job_json_data(job_list: list):
    """Formats and returns list of jobs to print.

    :param job_list: list of jobs
    :type job_list: list
    :return: formatted list of jobs
    :rtype: list
    """
    output_data = []

    for job in job_list:
        try:
            main_container_name = "custom-job"
            try:
                main_container = [
                    x
                    for x in job.get("containers", [])
                    if x.get("name") == main_container_name
                ][0]
            except IndexError:
                raise Exception(
                    "Parser was unable to find main container in server output in container list"
                )
            volumes_mounted = list_get_mounted_volumes(main_container.get("mounts", []))
            limits = main_container.get("resources", {}).get("limits")
            cpu = limits.get("cpu") if limits is not None else 0
            ram = limits.get("memory") if limits is not None else "0Gi"

            job_data = {
                "name": job.get("labels", {}).get("app-name"),
                "status": job.get("status", {}).get("phase", "Unknown"),
                "volumes_mounted": volumes_mounted,
                "cpu": cpu,
                "ram": ram,
            }
            # getting rid of unwanted and used values
            if "pod-template-hash" in job["labels"].keys():
                job["labels"].pop("pod-template-hash")
            job["labels"].pop("entity")

            # appending the rest of labels
            job_data.update(job["labels"])
            output_data.append(job_data)
        except KeyError:
            pass

    return output_data


def get_job_list(job_list: list, job_pod_list: list):
    list_of_json_job_data = get_job_json_data(job_list)

    for i, job_data in enumerate(job_list):
        list_of_json_job_data[i]["name"] = job_data.get("name", "")
        list_of_json_job_data[i]["ttl"] = job_data.get(
            "ttl_seconds_after_finished", "N/A"
        )
        list_of_json_job_data[i]["ads"] = job_data.get("active_deadline_seconds", "N/A")
    for job in list_of_json_job_data:
        for job_pod in job_pod_list:
            job_pod_labels: dict = job_pod.get("labels", {})
            print(job_pod.get("labels"))
            if job_pod_labels.get("app-name", "") == job.get("name"):
                if job["status"] is not None and job["status"] == "Unknown":
                    job["status"] = job_pod["status"]  # try to get status from pod
                elif job["status"] is None:  # support older server versions
                    job["status"] = job_pod["status"]
                job["gpu-count"] = job_pod_labels.get("gpu-count", 0)
                job["gpu-label"] = job_pod_labels.get("gpu-label", "N/A")
                break

    return list_of_json_job_data


def main():
    import json

    with open("test.json") as f:
        response_data = json.load(f)

    job_list = response_data.get("details", {}).get("job_list", [])
    job_pod_list = response_data.get("details", {}).get("job_pod_list", [])

    _list_of_json_job_data = get_job_list(job_list, job_pod_list)

    # print(list_of_json_job_data)


if __name__ == "__main__":
    main()
