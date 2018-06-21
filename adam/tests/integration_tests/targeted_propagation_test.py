from adam import Service
from adam import Batch
from adam import PropagationParams
from adam import OpmParams
from adam import BatchRunManager
from adam import ConfigManager
from adam import TargetedPropagation
from adam import TargetedPropagations
from adam import TargetingParams

import unittest
import datetime
import os

import numpy.testing as npt


class TargetedPropagationTest(unittest.TestCase):

    def setUp(self):
        config = ConfigManager(os.getcwd() + '/test_config.json').get_config()
        self.service = Service(config)
        self.assertTrue(self.service.setup())
        self.working_project = self.service.new_working_project()
        self.assertIsNotNone(self.working_project)

    def tearDown(self):
        self.service.teardown()

    def new_targeted_propagation(self):
        now = datetime.datetime.utcnow()
        later = now + datetime.timedelta(10 * 365)

        propagation_params = PropagationParams({
            'start_time': now.isoformat() + 'Z',
            'end_time': later.isoformat() + 'Z',
            'step_size': 60 * 60,  # 1 hour.
            'project_uuid': self.working_project.get_uuid(),
            'description': 'Created by test at ' + str(now) + 'Z'
        })

        state_vec = [130347560.13690618,
                     -74407287.6018632,
                     -35247598.541470632,
                     23.935241263310683,
                     27.146279819258538,
                     10.346605942591514]
        opm_params = OpmParams({
            'epoch': now.isoformat() + 'Z',
            'state_vector': state_vec,

            'mass': 500.5,
            'solar_rad_area': 25.2,
            'solar_rad_coeff': 1.2,
            'drag_area': 33.3,
            'drag_coeff': 2.5,

            'originator': 'Test',
            'object_name': 'TestObj',
            'object_id': 'TestObjId',
        })

        return propagation_params, opm_params, TargetingParams(
            {'target_distance_from_earth': 1e7})

    def test_targeted_propagation(self):
        propagation_params, opm_params, targeting_params = self.new_targeted_propagation()

        props = TargetedPropagations(self.service.rest)

        uuid = props.new_targeted_propagation(
            propagation_params, opm_params, targeting_params, self.working_project.get_uuid())
        self.assertIsNotNone(uuid)

        runnable_state = props.get_runnable_state(uuid)
        self.assertEqual('FAILED', runnable_state.get_calc_state())
        self.assertIsNotNone(runnable_state.get_error())

        runnable_state_list = props.get_runnable_states(
            self.working_project.get_uuid())
        self.assertEqual(1, len(runnable_state_list))

        props.delete(uuid)

        self.assertIsNone(props.get_targeted_propagation(uuid))


if __name__ == '__main__':
    unittest.main()
