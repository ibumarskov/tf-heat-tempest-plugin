from tempest.lib import decorators

from tf_heat_tempest_plugin.tests.functional import base


class AccessControlListTest(base.FunctionalTestsBase):

    @decorators.idempotent_id('9d37bfea-0a5b-11ec-89f7-d5b7da177e1b')
    def test_template_access_control_list(self):
        pass
