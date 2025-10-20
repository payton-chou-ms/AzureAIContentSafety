#
# Copyright (c) Microsoft. All rights reserved.
# To learn more, please visit the documentation - Quickstart: Azure Content Safety: https://aka.ms/acsstudiodoc
#

import enum
import requests


class TaskType(enum.Enum):
    SUMMARIZATION = "SUMMARIZATION"
    QNA = "QNA"


class DomainType(enum.Enum):
    MEDICAL = "MEDICAL"
    GENERIC = "GENERIC"


class ResourceType(enum.Enum):
    AZUREOPENAI = "AzureOpenAI"


class LLMResource:
    def __init__(self, openai_endpoint, openai_deployment_name):
        self.llm_resource={
            "resourceType": ResourceType.AZUREOPENAI.value,
            "azureOpenAIEndpoint": openai_endpoint,
            "azureOpenAIDeploymentName": openai_deployment_name
        }

def detect_groundness_body(
    domain: DomainType,
    task_type: TaskType,
    content_text: str,
    grounding_sources: list,
    query: str,
    reasoning: bool,
    llm_resource: LLMResource
) -> dict:
    """
    Builds the request body for the Content Safety API request.

    Args:
    - task_type (TaskType): The type of task to be analyzed.
    - content_text (str): The content to analyze.
    - groundingSources (list): The grounding sources to be analyzed.
    - query (str): The query to be analyzed.
    - reasoning (ReasoningType): Specifies whether to use the reasoning feature.
    - llm_resource (llmResource):GPT resources to provide an explanation.

    Returns:
    - dict: The request body for the Content Safety API request.
    """
    body = {
        "domain": domain.value,
        "task": task_type.value,
        "text": content_text,
        "groundingSources": grounding_sources,
        "Reasoning": reasoning
    }
    # For task type "QnA", the query value needs to be re-added.
    if task_type == TaskType.QNA:
        body["qna"] = {"query": query}
    # For reasoning true, the body needs add llmResource.
    if reasoning == True:
        body["llmResource"] = llm_resource.llm_resource
    return body


def detect_groundness_result(
    data: dict,
    url: str,
    subscription_key: str
):
    """
    Retrieve the Content Safety API request result.

    Args:
    - data (dict): The body data sent in the request.
    - url (str): The URL address of the request being sent.
    - subscription_key (str): The subscription key value corresponding to the request being sent.

    Returns:
    - response: The request result of the Content Safety API.
    """
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": subscription_key
    }

    # Send the API request
    response = requests.post(url, headers=headers, json=data)
    return response


if __name__ == "__main__":
    # Replace with your own subscription_key and endpoint
    subscription_key = "<your_subscription_key>"
    endpoint = "<your_resource_endpoint>"

    api_version = "2024-09-15-preview"

    # Set according to the actual task category.
    domain = DomainType.GENERIC
    task_type = TaskType.SUMMARIZATION
    content_text = "<test_content>"
    grounding_sources = [
        "<this_is_a_grounding_source>",
        "<this_is_another_grounding_source>"
    ]
    # When the task type value is "QnA", a test query needs to be added.
    query = "<test_query>"

    # Set reasoning type[True or False].
    reasoning = True
    # GPT resources to provide an explanation
    openai_endpoint = "<openai_endpoint>"
    deployment_name = "<openai_deployment_name>"
    llm_resource_instance = LLMResource(openai_endpoint=openai_endpoint, openai_deployment_name=deployment_name)

    # Build the request body
    data = detect_groundness_body(domain=domain, task_type=task_type, content_text=content_text,
                                  grounding_sources=grounding_sources, query=query, reasoning=reasoning, llm_resource=llm_resource_instance)

    # Set up the API request
    url = f"{endpoint}/contentsafety/text:detectGroundedness?api-version={api_version}"

    # Send the API request
    response = detect_groundness_result(data=data, url=url, subscription_key=subscription_key)

    # Handle the API response
    if response.status_code == 200:
        result = response.json()
        print("Groundedness result:", result)
    else:
        print("Error:", response.status_code, response.text)
