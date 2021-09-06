from tempest.lib import decorators

from tf_heat_tempest_plugin.tests.functional import base


class BgpRouterTest(base.FunctionalTestsBase):
    skip_check = ['fq_name', 'routing_instance']

    @decorators.idempotent_id('1c57f71a-0fa5-11ec-a578-07b1c8c5404b')
    def test_template_bgp_router(self):
        # Get default routing-instance
        routing_instances = self.routing_client.list_routing_instances()
        for instance in routing_instances['routing-instances']:
            if all(x in instance['fq_name'] for x in
                   ["ip-fabric", "__default__"]):
                ri_uuid = instance['uuid']
                break

        template = self.read_template('bgp_router_heat.yaml')
        resource_name = "template_BgpRouter"
        parameters = {
            'name': "BgpRouterTest",
            'display_name': "BgpRouterTest",
            'fq_name': "fq_name_BgpRouterTest",
            'bgp_router_parameters_admin_down': False,
            'bgp_router_parameters_vendor': 'juniper',
            'bgp_router_parameters_autonomous_system': 65000,
            'bgp_router_parameters_identifier': '10.10.10.10',
            'bgp_router_parameters_address': '10.10.10.10',
            'bgp_router_parameters_port': 179,
            'bgp_router_parameters_hold_time': 66,
            'bgp_router_parameters_address_families_family': 'inet',
            'bgp_router_parameters_local_autonomous_system': 64000,
            'bgp_router_parameters_router_type': 'router',
            'routing_instance': ri_uuid,
        }

        stack_identifier = self.create_stack(template, parameters=parameters)
        stack_id = stack_identifier.split('/')[1]
        self.client.wait_for_stack_status(stack_id, 'CREATE_COMPLETE')

        # Check TungstenFabric object
        body = self.client.show_resource(stack_identifier, resource_name)
        uuid = body['resource'].get('physical_resource_id')
        obj = self.router_client.show_bgp_router(uuid)
        self.check_tf_obj(template, resource_name, parameters,
                          obj['bgp-router'])
