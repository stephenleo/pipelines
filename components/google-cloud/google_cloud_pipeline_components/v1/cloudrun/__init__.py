# fmt: off
"""Deploy models on [Cloud Run](https://cloud.google.com/run)."""
# fmt: on

from google_cloud_pipeline_components.v1.cloudrun.component import (
    cloud_run_deploy as CloudRunDeployOp,
)

__all__ = [
    'CloudRunDeployOp'
]
