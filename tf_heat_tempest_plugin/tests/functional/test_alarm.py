from tempest.lib import decorators

from tf_heat_tempest_plugin.tests.functional import base

from oslo_log import log as logging
LOG = logging.getLogger(__name__)


class AlarmTest(base.FunctionalTestsBase):
    @decorators.idempotent_id('7d8914d2-0eed-11ec-9db2-892d1f23b370')
    def test_template_alarm(self):
        template = self.read_template('alarm_heat.yaml')
        parameters = {
            'name': "AlarmTest",
            'display_name': "AlarmTest",
            'fq_name': "fq_name_AlarmTest",
            'alarm_severity': 0,
            'rule_operation': '!=',
            'rule_operand1':
                'NodeStatus.process_info.process_state',
            'rule_operand2_uve_attr': 'Functional',
            'rule_vars': 'process_name',
            'uve_keys': ['service-instance'],
            'global_system_config': 'default-global-system-config',
            'project': self.os_admin.credentials.project_name
        }

        stack_identifier = self.create_stack(template, parameters=parameters)
        stack_id = stack_identifier.split('/')[1]
        self.client.wait_for_stack_status(stack_id, 'CREATE_COMPLETE')

        # Check TungstenFabric object
        body = self.client.show_resource(stack_identifier,
                                         'template_Alarm')
        uuid = body['resource'].get('physical_resource_id')
        obj = self.alarm_client.show_alarm(uuid)

        alarm_rule = obj['alarm']['alarm_rules']['or_list'][0]['and_list'][0]

        self.assertEqual(alarm_rule['operation'],
                         parameters['rule_operation'])
        self.assertEqual(alarm_rule['operand1'],
                         parameters['rule_operand1'])
        self.assertEqual(alarm_rule['operand2']['uve_attribute'],
                         parameters['rule_operand2_uve_attr'])
