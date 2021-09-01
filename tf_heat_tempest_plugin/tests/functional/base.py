import os
import yaml

from tempest import config
from tempest import test
from tempest.lib.services import clients
from tempest.lib.common.utils import data_utils
from tempest.lib.common.utils import test_utils

CONF = config.CONF


class FunctionalTestsBase(test.BaseTestCase):
    credentials = ['admin']

    @classmethod
    def skip_checks(cls):
        super(FunctionalTestsBase, cls).skip_checks()
        if not CONF.service_available.heat:
            raise cls.skipException("Heat support is required")
        if not CONF.service_available.tungstenfabric:
            raise cls.skipException("TungstenFabric isn't installed")

    @classmethod
    def setup_credentials(cls):
        cls.set_network_resources()
        super(FunctionalTestsBase, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(FunctionalTestsBase, cls).setup_clients()
        srv_clients = clients.ServiceClients(cls.os_admin.credentials,
                                             CONF.heat_plugin.auth_url)
        cls.client = srv_clients.heat_service.OrchestrationClient()

    @classmethod
    def resource_setup(cls):
        super(FunctionalTestsBase, cls).resource_setup()
        cls.stacks = []

    @classmethod
    def create_stack(cls, template_data, parameters=None,
                     environment=None, files=None):
        if parameters is None:
            parameters = {}
        stack_name = data_utils.rand_name('tf-heat')
        body = cls.client.create_stack(
            stack_name,
            template=template_data,
            parameters=parameters,
            environment=environment,
            files=files)
        stack_id = body.response['location'].split('/')[-1]
        stack_identifier = '%s/%s' % (stack_name, stack_id)
        cls.stacks.append(stack_identifier)
        return stack_identifier

    @classmethod
    def _clear_stacks(cls):
        for stack_identifier in cls.stacks:
            test_utils.call_and_ignore_notfound_exc(
                cls.client.delete_stack, stack_identifier)

        for stack_identifier in cls.stacks:
            test_utils.call_and_ignore_notfound_exc(
                cls.client.wait_for_stack_status, stack_identifier,
                'DELETE_COMPLETE')

    @classmethod
    def read_template(cls, name):
        loc = ["templates", name]
        fullpath = os.path.join(os.path.dirname(__file__), *loc)

        with open(fullpath, "r") as f:
            content = f.read()
            return content

    @classmethod
    def load_template(cls, name):
        loc = ["templates", name]
        fullpath = os.path.join(os.path.dirname(__file__), *loc)

        with open(fullpath, "r") as f:
            return yaml.safe_load(f)

    @classmethod
    def resource_cleanup(cls):
        cls._clear_stacks()
        super(FunctionalTestsBase, cls).resource_cleanup()
