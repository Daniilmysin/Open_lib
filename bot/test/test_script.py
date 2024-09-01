from bot.scripts import transliterate
import unittest


class MyTestCase(unittest.TestCase):
    async def transliter_test(self):
        self.assertEqual(await transliterate('текст тестовый 123'), 'tekst_testovyy_123')


if __name__ == '__main__':
    unittest.main()
