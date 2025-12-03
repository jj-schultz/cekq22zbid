import json
import tempfile
from pathlib import Path
from django.test import TestCase
from django.utils import timezone

from api.comment_manager import import_comments
from api.models import Comment, Person


class CommentImportTestCase(TestCase):
    def setUp(self):
        self.test_data = {
            "comments": [
                {
                    "id": "1",
                    "author": "Alice",
                    "text": "First test comment",
                    "date": "2023-01-01T10:00:00Z",
                    "likes": 10,
                    "image": "https://example.com/image1.jpg"
                },
                {
                    "id": "2",
                    "author": "Bob",
                    "text": "Second test comment",
                    "date": "2023-01-02T11:00:00Z",
                    "likes": 25,
                    "image": ""
                },
                {
                    "id": "3",
                    "author": "Alice",
                    "text": "Third test comment by Alice",
                    "date": "2023-01-03T12:00:00Z",
                    "likes": 5,
                    "image": "https://example.com/image3.jpg"
                }
            ]
        }

    def test_import_comments_basic(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_data, f)
            temp_file_path = Path(f.name)

        import_comments(temp_file_path)

        self.assertEqual(Comment.objects.count(), 3)
        self.assertEqual(Person.objects.count(), 3)

        comment1 = Comment.objects.get(id="1")
        self.assertEqual(comment1.text, "First test comment")
        self.assertEqual(comment1.author.name, "Alice")
        self.assertEqual(comment1.likes, 10)
        self.assertEqual(comment1.image, "https://example.com/image1.jpg")

        comment2 = Comment.objects.get(id="2")
        self.assertEqual(comment2.text, "Second test comment")
        self.assertEqual(comment2.author.name, "Bob")
        self.assertEqual(comment2.likes, 25)
        self.assertEqual(comment2.image, "")

        alice = Person.objects.get(name="Alice")
        alice_comments = Comment.objects.filter(author=alice)
        self.assertEqual(alice_comments.count(), 2)

        temp_file_path.unlink()

    def test_import_comments_creates_admin(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_data, f)
            temp_file_path = Path(f.name)

        import_comments(temp_file_path)

        admin = Person.objects.filter(name="Admin")
        self.assertTrue(admin.exists())

        temp_file_path.unlink()

    def test_import_comments_with_reset(self):
        existing_person = Person.objects.create(name="ExistingUser")
        existing_comment = Comment.objects.create(
            id="existing-1",
            author=existing_person,
            text="Existing comment",
            created_date=timezone.now(),
            updated_date=timezone.now(),
            likes=0,
            image=""
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_data, f)
            temp_file_path = Path(f.name)

        import_comments(temp_file_path, reset=True)

        self.assertEqual(Comment.objects.count(), 3)
        self.assertFalse(Comment.objects.filter(id="existing-1").exists())

        temp_file_path.unlink()

    def test_import_comments_without_reset(self):
        existing_person = Person.objects.create(name="ExistingUser")
        existing_comment = Comment.objects.create(
            id="existing-1",
            author=existing_person,
            text="Existing comment",
            created_date=timezone.now(),
            updated_date=timezone.now(),
            likes=0,
            image=""
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_data, f)
            temp_file_path = Path(f.name)

        import_comments(temp_file_path, reset=False)

        self.assertEqual(Comment.objects.count(), 4)
        self.assertTrue(Comment.objects.filter(id="existing-1").exists())

        temp_file_path.unlink()

    def test_import_comments_update_existing(self):
        alice = Person.objects.create(name="Alice")
        Comment.objects.create(
            id="1",
            author=alice,
            text="Original text",
            created_date=timezone.now(),
            updated_date=timezone.now(),
            likes=0,
            image=""
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_data, f)
            temp_file_path = Path(f.name)

        import_comments(temp_file_path)

        self.assertEqual(Comment.objects.count(), 3)

        comment1 = Comment.objects.get(id="1")
        self.assertEqual(comment1.text, "First test comment")
        self.assertEqual(comment1.likes, 10)

        temp_file_path.unlink()

    def test_import_comments_file_not_found(self):
        with self.assertRaises(ValueError) as context:
            import_comments(Path("/nonexistent/path/file.json"))

        self.assertIn("does not exist", str(context.exception))

    def test_import_comments_no_comments_field(self):
        bad_data = {"data": []}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(bad_data, f)
            temp_file_path = Path(f.name)

        with self.assertRaises(ValueError) as context:
            import_comments(temp_file_path)

        self.assertIn("no comments found", str(context.exception))

        temp_file_path.unlink()

    def test_import_comments_empty_comments_list(self):
        empty_data = {"comments": []}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(empty_data, f)
            temp_file_path = Path(f.name)

        with self.assertRaises(ValueError) as context:
            import_comments(temp_file_path)

        self.assertIn("no comments found", str(context.exception))

        temp_file_path.unlink()

    def test_import_comments_preserves_person_ids(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_data, f)
            temp_file_path = Path(f.name)

        import_comments(temp_file_path)

        alice = Person.objects.get(name="Alice")
        alice_id = alice.id

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f2:
            json.dump(self.test_data, f2)
            temp_file_path2 = Path(f2.name)

        import_comments(temp_file_path2)

        alice_after = Person.objects.get(name="Alice")
        self.assertEqual(alice_id, alice_after.id)

        temp_file_path.unlink()
        temp_file_path2.unlink()
