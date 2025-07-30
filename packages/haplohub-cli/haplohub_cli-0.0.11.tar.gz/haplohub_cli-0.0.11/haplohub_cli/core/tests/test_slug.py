from unittest import TestCase

from haplohub_cli.core.slug import slugify


class SlugifyTestCase(TestCase):
    def test_slugify_should_return_lowercase_string(self):
        self.assertEqual(slugify("Hello World"), "hello-world")

    def test_slugify_should_replace_spaces_with_hyphens(self):
        self.assertEqual(slugify("Hello World"), "hello-world")

    def test_slugify_should_remove_special_characters(self):
        self.assertEqual(slugify("Hello World!"), "hello-world")

    def test_slugify_should_remove_extra_spaces(self):
        self.assertEqual(slugify("Hello   World"), "hello-world")

    def test_slugify_should_keep_unchanged_when_no_changes_are_needed(self):
        self.assertEqual(slugify("hello-world"), "hello-world")
