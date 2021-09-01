from tempest import config
from tempest import test

CONF = config.CONF


class FunctionalTestsBase(test.BaseTestCase):

    def setUp(self):
        super(FunctionalTestsBase, self).setUp()

    @classmethod
    def skip_checks(cls):
        super(FunctionalTestsBase, cls).skip_checks()
        if CONF.get('sdn').get('service_name') != "tungstenfabric":
            raise cls.skipException("TungstenFabric isn't installed")
