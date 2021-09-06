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
        cls.access_control_client = \
            srv_clients.tf_service.AccessControlClient()
        cls.domain_client = srv_clients.tf_service.DomainClient()
        cls.alarm_client = srv_clients.tf_service.AlarmClient()
        # cls.vm_client = VmContrailClient()
        # cls.dsa_client = DiscoveryServiceAssignmentClient()
        # cls.dsa_rule_client = DSARuleClient()
        # cls.forwarding_class_client = ForwardingClassClient()
        # cls.qos_client = QosContrailClient()
        # cls.routing_client = RoutingClient()
        # cls.security_group_client = SecurityGroupClient()
        # cls.service_appliances_client = ServiceAppliancesClient()
        # cls.analytics_node_client = AnalyticsNodeClient()
        # cls.vn_client = VirtualNetworkClient()
        # cls.db_client = ContrailDatabaseClient()
        # cls.fip_client = FloatingIpClient()
        # cls.fq_client = FqnameIdClient()
        # cls.virtual_ip_client = VirtualIPClient()
        # cls.virtual_dns_client = VirtualDNSClient()
        # cls.domain_client = DomainClient()
        # cls.project_client = ProjectClient()
        # cls.port_tuple_client = PortTupleClient()
        # cls.network_policy_client = NetworkPolicyClient()
        # cls.routing_policy_client = RoutingPolicyClient()
        # cls.namespace_client = NamespaceClient()
        # cls.network_ipams_client = NetworkIpamsClient()
        # cls.bgp_as_a_service_client = BGPAsAServiceClient()
        # cls.iip_client = InstanceIPClient()
        # cls.subnet_client = SubnetClient()
        # cls.load_balancer_client = LoadBalancerClient()
        # cls.route_client = RouteClient()
        # cls.interface_client = InterfaceClient()
        # cls.router_client = RouterClient()
        # cls.service_client = ServiceClient()

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
