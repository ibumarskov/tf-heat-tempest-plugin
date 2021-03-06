# Copyright 2015
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import os

from tempest import config
from tempest.test_discover import plugins

from tf_heat_tempest_plugin import config as project_config


class TfHeatTempestPlugin(plugins.TempestPlugin):
    def load_tests(self):
        base_path = os.path.split(os.path.dirname(
            os.path.abspath(__file__)))[0]
        test_dir = "tf_heat_tempest_plugin/tests"
        full_test_dir = os.path.join(base_path, test_dir)
        return full_test_dir, base_path

    def register_opts(self, conf):
        config.register_opt_group(conf, project_config.service_available_group,
                                  project_config.ServiceAvailableGroup)

    def get_opt_lists(self):
        pass

    def get_service_clients(self):
        heat_service_config = config.service_client_config('heat_plugin')
        params_heat_service = {
            'name': 'heat_service',
            'service_version': 'heat_service',
            'module_path': 'tempest.services.orchestration',
            'client_names': ['OrchestrationClient'],
        }
        params_heat_service.update(heat_service_config)
        return [params_heat_service]
