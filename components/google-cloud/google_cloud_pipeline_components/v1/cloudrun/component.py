from google_cloud_pipeline_components import _image
from google_cloud_pipeline_components.types.artifact_types import VertexModel
from kfp.dsl import (
    ConcatPlaceholder,
    ContainerSpec,
    Input,
    OutputPath,
    container_component,
)


@container_component
def cloud_run_deploy(
    model: Input[VertexModel],
    deployed_model_display_name: str,
    gcp_resources: OutputPath(str),
    port: int = 8080,
    health_route: str = "/health",
    predict_route: str = "/predict",
    memory: str = "512Mi",
):
    # fmt: off
    """[Deploys](https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.endpoints/deployModel) a Google Cloud Vertex Model to an [Endpoint](https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.endpoints) creating a [DeployedModel](https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.endpoints#deployedmodel) within it. See the [deploy Model](https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.endpoints/deployModel) method for more information.

    Args:
        model: The model to be deployed.
        deployed_model_display_name: The display name of the deployed model in cloud run.
        port: The port to use for the cloud run service. Defaults to 8080. This will be passed to the inference docker container as an environment variable `AIP_HTTP_PORT`.
        health_route: The route to use for health checks. Defaults to '/health'. This will be passed to the inference docker container as an environment variable `AIP_HEALTH_ROUTE`.
        predict_route: The route to use for predictions. Defaults to '/predict'. This will be passed to the inference docker container as an environment variable `AIP_PREDICT_ROUTE`.
        memory: The memory limit to allocate for the cloud run service. Defaults to '512Mi'.

    Returns:
        gcp_resources: Serialized JSON of `gcp_resources` [proto](https://github.com/kubeflow/pipelines/tree/master/components/google-cloud/google_cloud_pipeline_components/proto) which tracks the deploy Model's long-running operation.
    """
    # fmt: on
    return ContainerSpec(
        image="us-central1-docker.pkg.dev/mlops-on-gcp-12345/stanfordnlp-imdb/cloud_run_deploy:latest",
        command=[
            "python3",
            "-u",
            "-m",
            "google_cloud_pipeline_components.container.v1.cloudrun.launcher",
        ],
        args=[
            "--type",
            "DeployModel",
            "--payload",
            ConcatPlaceholder(
                [
                    "{",
                    '"deployed_model_display_name": "',
                    deployed_model_display_name,
                    '"',
                    ', "model": "',
                    model.metadata["resourceName"],
                    '"',
                    ', "port": "',
                    str(port),
                    ', "health_route": "',
                    health_route,
                    ', "predict_route": "',
                    predict_route,
                    ', "memory": "',
                    memory,
                    '"}',
                ]
            ),
            "--project",
            "",
            "--location",
            "",
            "--gcp_resources",
            gcp_resources,
        ],
    )
