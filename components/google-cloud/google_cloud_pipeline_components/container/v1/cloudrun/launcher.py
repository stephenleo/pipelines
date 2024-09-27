import json
import logging
import re
import sys

import google.cloud.aiplatform as aip
from google.api_core import exceptions
from google.cloud import run_v2
from google_cloud_pipeline_components.container.v1.gcp_launcher.utils import (
    json_util,
    parser_util,
)

_CLOUDRUN_NAME_TEMPLATE = r"(projects/(?P<project>.*)/locations/(?P<location>.*)/models/(?P<model>.*)@(?P<version>.*))"


def _parse_args(args):
    """Parse command line arguments."""
    _, parsed_args = parser_util.parse_default_args(args)
    return vars(parsed_args)


def main(argv):
    aip.init()

    parsed_args = _parse_args(argv)

    deploy_model_request = json_util.recursive_remove_empty(
        json.loads(parsed_args["payload"], strict=False)
    )

    model = deploy_model_request["model"]
    model_info = aip.Model(model).gca_resource

    uri_pattern = re.compile(_CLOUDRUN_NAME_TEMPLATE)
    match = uri_pattern.match(model)
    try:
        project_id = match.group("project")
        location = match.group("location")
    except AttributeError as err:
        raise ValueError(
            "Invalid endpoint name: {}. Expect: {}.".format(
                model,
                "projects/[project_id]/locations/[location]",
            )
        )

    client = run_v2.ServicesClient()

    service = run_v2.Service(
        template=run_v2.RevisionTemplate(
            containers=[
                run_v2.Container(
                    image=model_info.container_spec.image_uri,
                    resources=run_v2.ResourceRequirements(
                        limits={"memory": deploy_model_request["memory"]}
                    ),
                    env=[
                        run_v2.EnvVar(name="AIP_HTTP_PORT", value=deploy_model_request["port"]),
                        run_v2.EnvVar(
                            name="AIP_STORAGE_URI", value=model_info.artifact_uri
                        ),
                        run_v2.EnvVar(name="AIP_HEALTH_ROUTE", value=deploy_model_request["health_route"]),
                        run_v2.EnvVar(name="AIP_PREDICT_ROUTE", value=deploy_model_request["predict_route"]),
                    ],
                )
            ],
        )
    )

    service_name = deploy_model_request["deployed_model_display_name"]
    service_name_full = (
        f"projects/{project_id}/locations/{location}/services/{service_name}"
    )

    try:
        existing_service = client.get_service(name=service_name_full)
        logging.info(f"Service {service_name} found. Updating to a new revision.")
        operation = client.update_service(service=existing_service)
    except exceptions.NotFound:
        logging.info(f"Service {service_name} not found. Creating a new service.")
        operation = client.create_service(
            parent=f"projects/{project_id}/locations/{location}",
            service_id=service_name,
            service=service,
        )

    operation.result(timeout=300)
    service = client.get_service(name=service_name_full)
    logging.info(f"Service deployed successfully. Service URL: {service.uri}")


if __name__ == "__main__":
    main(sys.argv[1:])
