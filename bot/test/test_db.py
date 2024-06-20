import logging
import unittest
from DBScripts import UserAct, BookAct, BDAct

logging.basicConfig(level=logging.INFO, filename="py_bot.log", format="%(asctime)s %(levelname)s %(message)s")

class SimpleUnitTest(unittest.TestCase):
    def test_user_act(self):
        self.assertEqual(True, UserAct.add_user(1111, "test"))
        self.assertEqual(True, UserAct.ban_user(1111, True))
        #self.assertEqual(True, UserAct.change_user(1111, )))
        self.assertEqual("test", UserAct.find_user(1111))


    def test_book_act(self):
        self.assertEqual(True, BookAct.BookAdd.name("test_book", 1111))
        self.assertEqual(True, BookAct.BookAdd.author_id(2222, 1111))
        self.assertEqual(True, BookAct.BookAdd.description("test_book", 1111))
        self.assertEqual(True, BookAct.BookAdd.end(1111))