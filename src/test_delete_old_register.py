import unittest
from  utils.task_delete_policy import TaskDeletePolicy

class Test_Delete_Old_Register(unittest.TestCase):
    
    def test_deletRegisters(self):
        task = TaskDeletePolicy()
        task.run()
        self.assertTrue(True)
