import io
from typing import Any, Literal, TypedDict, Union, overload
from urllib.parse import urlencode

import requests

from ..sdk import BaseCraftAiSdk
from ..shared.logger import log_func_result
from ..shared.request_response_handler import handle_http_response
from .deployments import get_deployment
from ..shared.authentication import use_authentication


def _get_endpoint_url_path(sdk: BaseCraftAiSdk, endpoint_name: str):
    deployment = get_deployment(sdk, endpoint_name)

    if deployment.get("execution_rule", "") != "endpoint":
        raise ValueError(f"Deployment {endpoint_name} is not an endpoint deployment")

    return deployment.get("endpoint_url_path", "")


class EndpointTriggerBase(TypedDict):
    execution_id: str


class EndpointTriggerWithOutputs(EndpointTriggerBase):
    outputs: dict[str, Any]


class EndpointNewToken(TypedDict):
    endpoint_token: str


@overload
def trigger_endpoint(
    sdk: BaseCraftAiSdk,
    endpoint_name: str,
    endpoint_token: str,
    inputs: dict[str, Any],
    wait_for_completion: Literal[True],
) -> EndpointTriggerWithOutputs: ...


@overload
def trigger_endpoint(
    sdk: BaseCraftAiSdk,
    endpoint_name: str,
    endpoint_token: str,
    inputs: dict[str, Any],
    wait_for_completion: Literal[False],
) -> EndpointTriggerBase: ...


@log_func_result("Endpoint trigger")
def trigger_endpoint(
    sdk: BaseCraftAiSdk,
    endpoint_name: str,
    endpoint_token: Union[str, None] = None,
    inputs: Union[dict[str, Any], None] = None,
    wait_for_completion=True,
) -> Union[EndpointTriggerWithOutputs, EndpointTriggerBase]:
    """Trigger an endpoint.

    Args:
        endpoint_name (:obj:`str`): Name of the endpoint.
        endpoint_token (:obj:`str`, optional): Token to access endpoint. If not set,
            the SDK token will be used.
        inputs (:obj:`dict`, optional): Dictionary of inputs to pass to the endpoint
            with input names as keys and corresponding values as values.
            For files, the value should be an instance of io.IOBase.
            For json, string, number, boolean and array inputs, the size of all values
            should be less than 0.06MB.
            Defaults to {}.
        wait_for_completion (:obj:`bool`, optional): Automatically call
            `retrieve_endpoint_results` and returns the execution result.
            Defaults to `True`.

    Returns:
        :obj:`dict`: Created pipeline execution represented as :obj:`dict` with the
        following keys:

        * ``"execution_id"`` (:obj:`str`): ID of the execution.
        * ``"outputs"`` (:obj:`dict`): Dictionary of outputs of the pipeline with
          output names as keys and corresponding values as values. Note that this
          key is only returned if ``wait_for_completion`` is `True`.
    """
    if inputs is None:
        inputs = {}

    body = {}
    files = {}
    for input_name, input_value in inputs.items():
        if isinstance(input_value, io.IOBase) and input_value.readable():
            files[input_name] = input_value
        else:
            body[input_name] = input_value

    if endpoint_token is None:
        url = (
            f"{sdk.base_environment_api_url}" f"/deployments/{endpoint_name}/executions"
        )
        do_post = use_authentication(
            lambda sdk, *args, **kwargs: sdk._session.post(*args, **kwargs)
        )
        post_result = do_post(
            sdk,
            url,
            allow_redirects=False,
            json=body,
            files=files,
        )

    else:
        endpoint_url_path = _get_endpoint_url_path(sdk, endpoint_name)
        url = f"{sdk.base_environment_url}/endpoints/{endpoint_url_path}"
        post_result = requests.post(
            url,
            headers={
                "Authorization": f"EndpointToken {endpoint_token}",
                "craft-ai-client": f"craft-ai-sdk@{sdk._version}",
            },
            allow_redirects=False,
            json=body,
            files=files,
        )
    response = handle_http_response(post_result)
    execution_id = response.get("execution_id", "")
    if wait_for_completion and 200 <= post_result.status_code < 400:
        return retrieve_endpoint_results(
            sdk,
            endpoint_name,
            execution_id,
            endpoint_token,
        )
    return {"execution_id": execution_id}


@log_func_result("Endpoint result retrieval")
def retrieve_endpoint_results(
    sdk: BaseCraftAiSdk,
    endpoint_name: str,
    execution_id: str,
    endpoint_token: Union[str, None] = None,
) -> EndpointTriggerWithOutputs:
    """Get the results of an endpoint execution.

    Args:
        endpoint_name (:obj:`str`): Name of the endpoint.
        execution_id (:obj:`str`): ID of the execution returned by
            `trigger_endpoint`.
        endpoint_token (:obj:`str`, optional): Token to access endpoint. If not set,
            the SDK token will be used.

    Returns:
        :obj:`dict`: Created pipeline execution represented as :obj:`dict` with the
        following keys:

        * ``"outputs"`` (:obj:`dict`): Dictionary of outputs of the pipeline with
          output names as keys and corresponding values as values.
    """

    if endpoint_token is None:
        return sdk.retrieve_pipeline_execution_outputs(execution_id)

    endpoint_url_path = _get_endpoint_url_path(sdk, endpoint_name)

    url = (
        f"{sdk.base_environment_url}"
        f"/endpoints/{endpoint_url_path}/executions/{execution_id}"
    )
    query = urlencode({"token": endpoint_token})
    response = requests.get(f"{url}?{query}")

    handled_response = handle_http_response(response)

    # 500 is returned if the pipeline failed too. In that case, it is not a
    # standard API error
    if response.status_code == 500:
        try:
            return handled_response
        except KeyError:
            return response.json()

    if "application/octet-stream" in response.headers.get("Content-Type", ""):
        content_disposition = response.headers.get("Content-Disposition", "")
        output_name = content_disposition.split(f"_{execution_id}_")[1]
        return {
            "outputs": {output_name: handled_response},
            "execution_id": execution_id,
        }
    else:
        response_data = handle_http_response(response)
        return {
            "outputs": response_data.get("outputs", []),
            "execution_id": execution_id,
        }


def generate_new_endpoint_token(
    sdk: BaseCraftAiSdk, endpoint_name: str
) -> EndpointNewToken:
    """Generate a new endpoint token for an endpoint.

    Args:
        endpoint_name (:obj:`str`): Name of the endpoint.

    Returns:
        :obj:`dict[str, str]`: New endpoint token represented as :obj:`dict` with
        the following keys:

        * ``"endpoint_token"`` (:obj:`str`): New endpoint token.
    """
    url = (
        f"{sdk.base_environment_api_url}"
        f"/endpoints/{endpoint_name}/generate-new-token"
    )
    return sdk._post(url)
