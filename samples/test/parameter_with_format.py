# Copyright 2021 The Kubeflow Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from kfp.deprecated import components
from kfp.deprecated import dsl


@components.create_component_from_func
def print_op(name: str) -> str:
    print(name)
    return name


@dsl.pipeline(name='pipeline-with-pipelineparam-containing-format')
def my_pipeline(name: str = 'KFP'):
    print_task = print_op('Hello {}'.format(name))
    # print_op('{}, again.'.format(print_task.output))
    print_op('{}, again.'.format(print_task.output))


if __name__ == '__main__':
    import datetime
    import warnings

    from google.cloud import aiplatform
    from kfp.deprecated import compiler

    warnings.filterwarnings('ignore')
    ir_file = __file__.replace('.py', '.yaml')
    compiler.Compiler().compile(pipeline_func=my_pipeline, package_path=ir_file)
    # aiplatform.PipelineJob(
    #     template_path=ir_file,
    #     pipeline_root='gs://cjmccarthy-kfp-default-bucket',
    #     display_name=str(datetime.datetime.now())).submit()
