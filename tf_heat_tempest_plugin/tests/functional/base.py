import os
import yaml

from oslo_log import log as logging
from tempest import config
from tempest import test
from tempest.lib.services import clients
from tempest.lib.common.utils import data_utils
from tempest.lib.common.utils import test_utils

CONF = config.CONF
LOG = logging.getLogger(__name__)


class FunctionalTestsBase(test.BaseTestCase):
    credentials = ['admin']
    skip_check = []

    @classmethod
    def skip_checks(cls):
        super(FunctionalTestsBase, cls).skip_checks()
        if not CONF.service_available.heat:
            raise cls.skipException("Heat support is required")
        if not CONF.service_available.contrail:
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
        cls.access_control_client = \
            srv_clients.tf_service.AccessControlClient()
        cls.domain_client = srv_clients.tf_service.DomainClient()
        cls.alarm_client = srv_clients.tf_service.AlarmClient()
        cls.vm_client = srv_clients.tf_service.VmContrailClient()
        cls.dsa_client = \
            srv_clients.tf_service.DiscoveryServiceAssignmentClient()
        cls.dsa_rule_client = srv_clients.tf_service.DSARuleClient()
        cls.forwarding_class_client = \
            srv_clients.tf_service.ForwardingClassClient()
        cls.qos_client = srv_clients.tf_service.QosContrailClient()
        cls.routing_client = srv_clients.tf_service.RoutingClient()
        cls.security_group_client = \
            srv_clients.tf_service.SecurityGroupClient()
        cls.service_appliances_client = \
            srv_clients.tf_service.ServiceAppliancesClient()
        cls.analytics_node_client = srv_clients.tf_service.AnalyticsNodeClient()
        cls.vn_client = srv_clients.tf_service.VirtualNetworkClient()
        cls.db_client = srv_clients.tf_service.ContrailDatabaseClient()
        cls.fip_client = srv_clients.tf_service.FloatingIpClient()
        cls.fq_client = srv_clients.tf_service.FqnameIdClient()
        cls.virtual_ip_client = srv_clients.tf_service.VirtualIPClient()
        cls.virtual_dns_client = srv_clients.tf_service.VirtualDNSClient()
        cls.domain_client = srv_clients.tf_service.DomainClient()
        cls.project_client = srv_clients.tf_service.ProjectClient()
        cls.port_tuple_client = srv_clients.tf_service.PortTupleClient()
        cls.network_policy_client = \
            srv_clients.tf_service.NetworkPolicyClient()
        cls.routing_policy_client = \
            srv_clients.tf_service.RoutingPolicyClient()
        cls.namespace_client = srv_clients.tf_service.NamespaceClient()
        cls.network_ipams_client = srv_clients.tf_service.NetworkIpamsClient()
        cls.bgp_as_a_service_client = \
            srv_clients.tf_service.BGPAsAServiceClient()
        cls.iip_client = srv_clients.tf_service.InstanceIPClient()
        cls.subnet_client = srv_clients.tf_service.SubnetClient()
        cls.load_balancer_client = srv_clients.tf_service.LoadBalancerClient()
        cls.route_client = srv_clients.tf_service.RouteClient()
        cls.interface_client = srv_clients.tf_service.InterfaceClient()
        cls.router_client = srv_clients.tf_service.RouterClient()
        cls.service_client = srv_clients.tf_service.ServiceClient()

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

    def check_tf_obj(self, template, resource, parameters, tfobj):
        yml = yaml.load(template)
        properties = yml['resources'][resource]['properties']
        for p_key, p_val in parameters.items():
            LOG.debug("Check template parameter '{}': '{}'".format(p_key,
                                                                   p_val))
            if p_key in self.skip_check:
                LOG.info("Validation of '{}' parameter was skipped."
                         "".format(p_key))
                continue
            attr_path = self.get_attr_path(properties, p_key, attr_path=[])
            tfobj_val = self.get_val_by_path(tfobj, attr_path)
            self.assertEqual(tfobj_val, p_val)

    @staticmethod
    def _child_has_param(obj, param):
        if obj['get_param'] == param:
            return True

    @staticmethod
    def _end_tree(obj):
        if type(obj) is not dict:
            return False
        if 'get_param' in obj:
            assert (len(obj.keys()) == 1)
            return True

    @staticmethod
    def _update_attr_path(path):
        new_path = []
        stored_val = None
        for i, val in enumerate(path):
            if not stored_val:
                stored_val = val
            key = val
            if type(val) is not int:
                if i < len(path) and val.startswith(stored_val):
                    key = val.replace(stored_val + "_", "")
                stored_val = val
            new_path.append(key)
        return new_path

    def _attr_path(self, obj, param, attr_path=[]):
        if self._end_tree(obj):
            if self._child_has_param(obj, param):
                return attr_path
            return
        if type(obj) is dict:
            for key in obj.keys():
                attr_path.append(key)
                if self._attr_path(obj[key], param, attr_path=attr_path):
                    return attr_path
                else:
                    attr_path.pop()
        elif type(obj) is list:
            assert (len(obj) == 1)
            attr_path.append(0)
            if self._attr_path(obj[0], param, attr_path=attr_path):
                return attr_path
            else:
                attr_path.pop()

    def get_attr_path(self, obj, param, attr_path=[]):
        attr_path = self._attr_path(obj, param, attr_path)
        LOG.debug("Attribute path: {}".format(attr_path))
        return self._update_attr_path(attr_path)

    @staticmethod
    def get_val_by_path(obj, attr_path):
        for attr in attr_path:
            obj = obj[attr]
        LOG.debug("TF object value: '{}'".format(obj))
        return obj
