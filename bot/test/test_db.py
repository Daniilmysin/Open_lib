import unittest
from DBScripts import UserAct, BookAct, BDAct, AuthorAct

author = AuthorAct().AuthorAdd()
BookAdd = BookAct().BookAdd()
bd = BDAct()


class SimpleUnitTest(unittest.TestCase):
    def test_bd_act(self):
        self.assertTrue(bd.del_db())
        self.assertTrue(bd.make_bd())

    def test_user_act(self):
        self.assertTrue(UserAct.add_user(1111, "test"))
        self.assertTrue(UserAct.ban_user(1111, True))
        self.assertTrue(UserAct.ban_user(1111, False))
        #self.assertTrue(UserAct.change_user(1111))
        #self.assertTrue(UserAct.find_user(1111))

    def test_author_act(self):
        self.assertTrue(author.name('иван иванович иванов', 1111))
        self.assertTrue(author.description('test', 1111))
        self.assertTrue(author.photo('test', 1111))
        self.assertTrue(author.end(1111))

    def test_book_act(self):
        self.assertTrue(BookAdd.name(name="test_book", id_user=1111))
        self.assertTrue(BookAdd.author_id(id_author=1111, id_user=1111))
        self.assertTrue(BookAdd.description(1111, 'des'))
        self.assertTrue(BookAdd.end(id_user=1111, epub='test'))
