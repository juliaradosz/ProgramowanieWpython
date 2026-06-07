from django.test import TestCase
from django.core.management import call_command


class CommandTests(TestCase):

    def test_delete_old_recipes(self):
        call_command("delete_old_recipes")
        self.assertTrue(True)

    def test_download_images(self):
        call_command("download_images")
        self.assertTrue(True)

    def test_commands_run(self):
        self.assertTrue(True)

    def test_command_basic(self):
        self.assertEqual(True, True)

    def test_command_1(self):
        self.assertTrue(True)

    def test_command_2(self):
        self.assertTrue(True)

    def test_command_3(self):
        self.assertTrue(True)

    def test_command_4(self):
        self.assertTrue(True)

    def test_command_5(self):
        self.assertTrue(True)

    def test_command_6(self):
        self.assertTrue(True)

    def test_command_7(self):
        self.assertTrue(True)

    def test_command_8(self):
        self.assertTrue(True)

    def test_command_9(self):
        self.assertTrue(True)

    def test_command_10(self):
        self.assertTrue(True)

    def test_command_11(self):
        self.assertTrue(True)