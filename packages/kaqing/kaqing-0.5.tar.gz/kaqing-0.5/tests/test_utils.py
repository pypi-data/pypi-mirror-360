import unittest
from walker.k8s_utils import get_host_id, is_pod_name, is_statefulset_name, strip, to_tabular

class TestUtils(unittest.TestCase):
    def test_get_host_id(self):
        self.assertIsNotNone(get_host_id('cs-d0767a536f-cs-d0767a536f-default-sts-0', 'gkeops845'))

    def test_to_tabular(self):
        lines = strip("""
            Unknown cs-d0767a536f-cs-d0767a536f-default-sts-0 Running
            6ebc023e-47fc-487a-9443-b05fbd343b4b cs-d0767a536f-cs-d0767a536f-default-sts-1 Running
            6eb3d978-d20b-4a01-9749-54f9b89388ca cs-d0767a536f-cs-d0767a536f-default-sts-2 Running
        """)

        print('\n' + to_tabular(lines))

    def test_is_pod_name(self):
        self.assertEqual(('cs-d0767a536f-cs-d0767a536f-default-sts-0', None), is_pod_name('cs-d0767a536f-cs-d0767a536f-default-sts-0'))
        self.assertEqual((None, None), is_pod_name('cs-d0767a536f-cs-d0767a536f-default-sts'))

    def test_is_statefulset_name(self):
        self.assertEqual((None, None), is_statefulset_name('cs-d0767a536f-cs-d0767a536f-default-sts-0'))
        self.assertEqual(('cs-d0767a536f-cs-d0767a536f-default-sts', None), is_statefulset_name('cs-d0767a536f-cs-d0767a536f-default-sts'))

if __name__ == '__main__':
    unittest.main()