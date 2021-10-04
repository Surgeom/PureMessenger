import unittest
import sys

sys.path.append('..')

from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR
from client import create_presence, process_ans


class ClientTestCase(unittest.TestCase):

    def test_def_presense(self):
        test = create_presence()
        test[TIME] = 1
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1, USER: {ACCOUNT_NAME: 'Guest'}, 'DATA': ""})
        print('test def_presense done')

    def test_200_ans(self):
        self.assertEqual(process_ans({RESPONSE: 200}), '200 : OK')
        print('test200 done')

    def test_400_ans(self):
        self.assertEqual(process_ans({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')
        print('test400 done')

    def test_no_response(self):
        self.assertRaises(ValueError, process_ans, {ERROR: 'Bad Request'})
        print('test400 no response')


if __name__ == '__main__':
    unittest.main()
