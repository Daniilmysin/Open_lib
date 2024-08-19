import logging
import unittest
from DBScripts import UserAct, BookAct, BDAct

logger = logging.getLogger('example_logger')
logger.setLevel(logging.DEBUG)

# Добавление обработчика для вывода логов в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)


class SimpleUnitTest(unittest.TestCase):
    def test_user_act(self):
        self.assertTrue( UserAct.add_user(1111, "test"))
        self.assertTrue(UserAct.ban_user(1111, True))
        self.assertTrue(UserAct.ban_user(1111, False))
        #self.assertTrue(UserAct.change_user(1111))
        #self.assertTrue(UserAct.find_user(1111))


    def test_book_act(self):
        with self.assertLogs('example_logger', level='DEBUG') as log:
            self.assertTrue(BookAct.BookAdd.name(name="test_book", id_user=1111))
            self.assertTrue(BookAct.BookAdd.author_id(id_author=1111, id_user=1111))
            self.assertTrue(BookAct.BookAdd.description(1111))
            self.assertTrue(BookAct.BookAdd.end(id_user=1111, epub='test'))
        for message in log.output:
            print(message)