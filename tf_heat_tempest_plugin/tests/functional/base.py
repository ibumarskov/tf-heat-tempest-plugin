import os
import yaml

from heatclient.common import template_utils
from tempest import config

from heat_tempest_plugin.common import test

CONF = config.CONF


class FunctionalTestsBase(test.HeatIntegrationTest):

    def setUp(self):
        super(FunctionalTestsBase, self).setUp()
        self.sub_dir = 'templates'
        self.check_skip()

    def check_skip(self):
        # TO DO:
        # if CONF.get('sdn').get('service_name') != "tungstenfabric":
        #     self.skipTest("TungstenFabric isn't installed")
        pass

    @staticmethod
    def _load_template(base_file, file_name, sub_dir=None, files=None):
        sub_dir = sub_dir or ''
        filepath = os.path.join(os.path.dirname(os.path.realpath(base_file)),
                                sub_dir, file_name)
        _files, template = template_utils.get_template_contents(filepath,
                                                                files=files)
        return yaml.safe_dump(template)

    def launch_stack(self, template_name, expected_status='CREATE_COMPLETE',
                     parameters=None, **kwargs):
        files = kwargs.get('files', {})
        template = self._load_template(__file__, template_name, self.sub_dir,
                                       files)

        stack_id = self.stack_create(
            stack_name=kwargs.get('stack_name'),
            template=template,
            files=files,
            parameters=parameters,
            environment=kwargs.get('environment'),
            expected_status=expected_status
        )

        return stack_id
