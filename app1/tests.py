from django.test import TestCase


class Simpleadd(TestCase):
    def test_addition(self):
        self.assertEqual(1 + 1, 2)
        self.assertEqual(5 + 5, 10)

class Simplesub(TestCase):
    def test_subtraction(self):
        self.assertEqual(1 - 2, -1)
        self.assertEqual(5 - 10, -5)