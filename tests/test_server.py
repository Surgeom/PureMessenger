import unittest
import sys

sys.path.append('..')
from server import process_client_message
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE

err_dict = {
    RESPONSE: 400,
    ERROR: 'Bad Request'
}
ok_dict = {RESPONSE: 200}


class ServerTestCase(unittest.TestCase):
    def test_bad_mes(self):
        self.assertEqual(process_client_message('nope'), err_dict)
        print('test bad mes done')

    def test_wrong_action(self):
        self.assertEqual(process_client_message(
            {ACTION: 'Wrong', TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), err_dict)

    def test_ok_check(self):
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), ok_dict)


if __name__ == '__main__':
    unittest.main()
