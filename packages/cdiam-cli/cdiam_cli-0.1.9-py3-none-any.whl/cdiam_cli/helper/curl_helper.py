import json
from typing import Any, Dict
import uuid
import os
import boto3


def _check_valid_uuid(uuid_str: str):
    # check if the uuid is valid
    try:
        uuid_obj = uuid.UUID(uuid_str)
        return str(uuid_obj) == uuid_str
    except ValueError:
        return False


def download_from_s3(s3_url: str, local_path: str):
    s3 = boto3.client("s3")
    bucket = s3_url.split("/")[2]
    key = "/".join(s3_url.split("/")[3:])
    s3.download_file(bucket, key, local_path)


def _convert(data: Any, ret: Dict[str, str], key: str, temp_dir: str):
    if isinstance(data, dict):
        for k in data.keys():
            _convert(data[k], ret, f"{key}[{k}]" if key != "" else k, temp_dir)
    elif isinstance(data, list):
        for index, k in enumerate(data):
            _convert(data[index], ret, f"{key}[{index}]", temp_dir)
    else:
        if data is not None:
            if key == "data_info[description]":
                try:
                    json.loads(data)
                except Exception as e:
                    print("Description is not a valid json string. Ignore it.")
                    return
            if key == "data_info[tags]":
                try:
                    json.loads(data)
                except Exception as e:
                    print("Tag is not a valid json string. Ignore it.")
                    return
            if key == "data_info[species]":
                if data not in [
                    "homo_sapiens",
                    "mus_musculus",
                    "rattus_norvegicus",
                    "sus_scrofa",
                ]:
                    raise Exception(
                        "Species is not a valid species. Should be one of the following: homo_sapiens, mus_musculus, rattus_norvegicus, sus_scrofa"
                    )

            if key == "data_info[force_index]":
                if data not in ["yes", "no"]:
                    raise Exception(
                        "Force index is not a valid boolean. Should be one of the following: yes, no"
                    )
            if key == "data_info[project_id]":
                if not _check_valid_uuid(data):
                    raise Exception("Project id is not a valid uuid")
            if key == "data_info[data_id]":
                if not _check_valid_uuid(data):
                    raise Exception("Data id is not a valid uuid")
            if key == "data_info[directory]":
                if not _check_valid_uuid(data):
                    raise Exception(
                        "Directory id is not a valid uuid. Consider remove this param"
                    )
            if data is not None and isinstance(data, str) and data.startswith("@"):
                if not os.path.exists(data[1:]):
                    raise Exception(f"File {data[1:]} does not exist")

            if data is not None and isinstance(data, str) and data.startswith("s3://"):
                temp_file = os.path.join(temp_dir, str(uuid.uuid4()))
                print(f"Downloading {data} to {temp_file}")
                download_from_s3(data, temp_file)
                ret[key] = f"@{temp_file}"
            else:
                ret[key] = data


def generate_curl_form_command(form_data: Dict[str, str], endpoint: str):
    command = [
        "curl",
        "-L",
        "-X",
        "POST",
        "-H",
        "Content-Type: multipart/form-data",
    ]
    for k, v in form_data.items():

        command.append("-F")
        if v is None or (isinstance(v, str) and v.startswith("@")):
            command.append(f'{k}={"null" if v is None  else v}')
        else:
            command.append(f'{k}="{v}"')

    command.append(endpoint)
    return command


def generate_curl_json_command(json_data: Dict[str, str], endpoint: str):
    command = [
        "curl",
        "-#",
        "-L",
        "-X",
        "POST",
        "-H",
        "Content-Type: application/json",
    ]
    command.append("-d")
    command.append(json.dumps(json_data))
    command.append(endpoint)
    return command


def convert_json_to_form_data(json_object: Any, temp_dir: str):
    ret = {}
    _convert(json_object, ret, "", temp_dir)
    return ret
