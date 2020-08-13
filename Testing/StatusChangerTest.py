import StatusChanger.StatusChanger as StatusChanger
from States.States import States
import unittest


class StatusChangerTest(unittest.TestCase):

    def test_motor(self):
        # start motor, slow
        StatusChanger.status_changer(132)
        self.assertTrue(States.MOTOR_STARTED)
        self.assertTrue(States.MOTOR_SLOW)
        self.assertFalse(States.MOTOR_FAST)

        # start motor, fast
        StatusChanger.status_changer(122)
        self.assertTrue(States.MOTOR_STARTED)
        self.assertTrue(States.MOTOR_FAST)
        self.assertFalse(States.MOTOR_SLOW)

        # stop motor
        StatusChanger.status_changer(192)
        self.assertFalse(States.MOTOR_STARTED)
        self.assertFalse(States.MOTOR_FAST)
        self.assertFalse(States.MOTOR_SLOW)

    def test_crane(self):
        # crane loading
        StatusChanger.status_changer(211)
        self.assertTrue(States.CRANE_LOADING)
        self.assertFalse(States.CRANE_LOADED)

        # crane loaded
        StatusChanger.status_changer(212)
        self.assertTrue(States.CRANE_LOADED)
        self.assertFalse(States.CRANE_LOADING)

    def test_ir1(self):
        StatusChanger.status_changer(312)
        self.assertTrue(States.IR_1_STARTED)

    def test_acceleration(self):
        StatusChanger.status_changer(512)
        self.assertTrue(States.ACCELERATION_STARTED)

    if __name__ == '__main__':
        unittest.main()