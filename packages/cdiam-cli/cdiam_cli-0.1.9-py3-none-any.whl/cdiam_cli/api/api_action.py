import json
import click
from cdiam_cli.helper import yaml_helper, curl_helper
import subprocess
from typing import Union, Callable, Any, Dict, overload, Literal
from .settings import read_api_endpoint, read_api_token
from cdiam_cli.schemas import ParamsRequestGetTaskStatus
from cdiam_cli.schemas.analysis import AnalysisResultRead, AnalysisResult
from time import sleep
from tempfile import TemporaryDirectory


def wait_task(task_id: str):
    while True:
        sleep(10)
        res = run(
            ParamsRequestGetTaskStatus(api="get_task_status", task_id=task_id).dict()
        )
        status = AnalysisResultRead(**res)

        if status.task is None:
            raise Exception("Task FAILURE")
        if status.task.status == "FAILURE":
            raise Exception("Task FAILURE")
        if status.task.status == "SUCCESS":
            break
    return status


def parse_and_wait_task(process: Any):
    analysis_result: AnalysisResult = AnalysisResult(**process)
    assert analysis_result.task_id is not None
    print(analysis_result)
    status = wait_task(task_id=analysis_result.task_id)
    print(status)
    return status


@overload
def run(
    params: Union[str, Dict[Any, Any]],
    modify_params_callback: Union[Callable[[Any], Any], None] = None,
    wait_as_analysis: Literal[False] = False,
) -> Any: ...
@overload
def run(
    params: Union[str, Dict[Any, Any]],
    modify_params_callback: Union[Callable[[Any], Any], None] = None,
    wait_as_analysis: Literal[True] = True,
) -> AnalysisResult: ...
def run(
    params: Union[str, Dict[Any, Any]],
    modify_params_callback: Union[Callable[[Any], Any], None] = None,
    wait_as_analysis: bool = False,
):
    """
    Runs an API call with the provided parameters and returns the API response.

    Args:
        params (Union[str, Dict[Any, Any]]): The API parameters, either as a path to a JSON or YAML file, or as a dictionary.
        More details about api schemas can be found in the documentation at https://c-diam.com/api/schemas/docs or if you are using different endpoint you can find it at https://<your-end-point>/api/schemas/docs.
        modify_params_callback (Union[Callable[[Any], Any], None]): An optional callback function to modify the API parameters before the call.
        wait_as_analysis (bool): If True, the function will wait for the API task to complete and return the analysis result.

    Returns:
        Any: The API response, or an AnalysisResult if wait_as_analysis is True.

    Raises:
        Exception: If the API call fails.
    """
    with TemporaryDirectory() as temp_dir:

        if isinstance(params, str):
            if params.endswith(".json"):
                with open(params) as f:
                    data = json.load(f)
            else:
                data = yaml_helper.read(params)
            if modify_params_callback is not None:
                data = modify_params_callback(data)
        else:
            data = params

        if "download_" in data["api"]:  # type: ignore
            if "output_path" not in data:  # type: ignore
                raise Exception("output_path is required in params")
            form_data = curl_helper.convert_json_to_form_data(data, temp_dir)
            command = curl_helper.generate_curl_json_command(
                form_data, endpoint=f"{read_api_endpoint()}/api_public/{data['api']}"  # type: ignore
            )
            command.append("-o")
            command.append(data["output_path"])  # type: ignore
        elif "upload_" in data["api"]:  # type: ignore
            form_data = curl_helper.convert_json_to_form_data(data, temp_dir)
            command = curl_helper.generate_curl_form_command(
                form_data, endpoint=f"{read_api_endpoint()}/api_public/{data['api']}"  # type: ignore
            )
        else:
            command = curl_helper.generate_curl_json_command(
                data, endpoint=f"{read_api_endpoint()}/api_public/{data['api']}"  # type: ignore
            )
        command.append("-b")
        command.append(f"cdiam_session_token={read_api_token()}")

        if "download_" in data["api"]:  # type: ignore
            process = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            # Check if the file is a JSON error response (instead of the expected file)
            with open(data["output_path"], "rb") as f:  # type: ignore
                head = f.read(1024 * 10)  # Read only first 1KB for quick check

            try:
                # Try parsing as JSON
                json_data = json.loads(head.decode("utf-8"))
                raise Exception(f"Server returned JSON error: {json_data}")
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Not JSON: assume it's the expected file → OK
                pass
        else:
            process = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        process.check_returncode()
        if not "download_" in data["api"]:  # type: ignore
            output = json.loads(process.stdout.decode())
        else:
            output = "Done"

    if "detail" in output:
        raise Exception(output)

    if wait_as_analysis:
        output = parse_and_wait_task(output)

    return output


@click.command()
@click.argument("params", type=click.Path(exists=True), required=True)
def call_api(params: str):
    """
    Calls the API with the provided parameters and returns the API response.

    Args:
        params (str): The path to a JSON or YAML file containing the API parameters. More details about api schemas can be found in the documentation at https://c-diam.com/api/schemas/docs or if you are using different endpoint you can find it at https://<your-end-point>/api/schemas/docs.
    Returns:
        str: The API response.

    Raises:
        Exception: If the API call fails.
    """

    data = run(params)
    print(json.dumps(data, indent=4, sort_keys=True))
