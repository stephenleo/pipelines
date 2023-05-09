# Copyright 2023 The Kubeflow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional

from google_cloud_pipeline_components.types.artifact_types import VertexDataset
from kfp import dsl
from kfp.dsl import Input
from kfp.dsl import Output


@dsl.container_component
def image_dataset_export(
    project: str,
    dataset: Input[VertexDataset],
    output_dir: str,
    exported_dataset: Output[VertexDataset],
    location: Optional[str] = 'us-central1',
):
  # fmt: off
  """
  Exports data to output dir to GCS.
  Args:
      output_dir (String):
          Required. The Google Cloud Storage location where the output is to
          be written to. In the given directory a new directory will be
          created with name:
          ``export-data-<dataset-display-name>-<timestamp-of-export-call>``
          where timestamp is in YYYYMMDDHHMMSS format. All export
          output will be written into that directory. Inside that
          directory, annotations with the same schema will be grouped
          into sub directories which are named with the corresponding
          annotations' schema title. Inside these sub directories, a
          schema.yaml will be created to describe the output format.
          If the uri doesn't end with '/', a '/' will be automatically
          appended. The directory is created if it doesn't exist.
      project (String):
          Required. project to retrieve dataset from.
      location (String):
          Optional location to retrieve dataset from.
  Returns:
      exported_files (Sequence[str]):
          All of the files that are exported in this export operation.

  """
  # fmt: on

  return dsl.ContainerSpec(
      image='gcr.io/ml-pipeline/google-cloud-pipeline-components:2.0.0b3',
      command=[
          'python3',
          '-m',
          'google_cloud_pipeline_components.container.aiplatform.remote_runner',
          '--cls_name',
          'ImageDataset',
          '--method_name',
          'export_data',
      ],
      args=[
          '--init.dataset_name',
          dataset.metadata['resourceName'],
          '--init.project',
          project,
          '--init.location',
          location,
          '--method.output_dir',
          output_dir,
          '--executor_input',
          '{{$}}',
          '--resource_name_output_artifact_uri',
          exported_dataset.uri,
      ],
  )
