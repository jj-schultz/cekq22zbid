import json
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from api.models import Comment, Person


class CommentCRUDTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.test_person = Person.objects.create(
            id=uuid.uuid4(),
            name="Admin"
        )

        self.existing_comment = Comment.objects.create(
            id=str(uuid.uuid4()),
            author=self.test_person,
            text="Existing test comment",
            created_date=timezone.now(),
            updated_date=timezone.now(),
            likes=0,
            image="https://example.com/image.jpg"
        )

    def test_get_all_comments_empty(self):
        """Test retrieving all comments when database has no comments"""
        Comment.objects.all().delete()

        response = self.client.get(reverse('get_all_comments'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('comments', data)
        self.assertEqual(len(data['comments']), 0)

    def test_get_all_comments_with_data(self):
        """Test retrieving all comments when database has comments"""
        response = self.client.get(reverse('get_all_comments'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('comments', data)
        self.assertEqual(len(data['comments']), 1)

        comment = data['comments'][0]
        self.assertEqual(comment['id'], self.existing_comment.id)
        self.assertEqual(comment['text'], "Existing test comment")
        self.assertEqual(comment['author']['name'], "Admin")
        self.assertEqual(comment['image'], "https://example.com/image.jpg")

    def test_get_all_comments_ordering(self):
        """Test that comments are returned in reverse chronological order"""
        older_comment = Comment.objects.create(
            id=str(uuid.uuid4()),
            author=self.test_person,
            text="Older comment",
            created_date=timezone.now() - timezone.timedelta(hours=1),
            updated_date=timezone.now() - timezone.timedelta(hours=1),
            likes=0,
            image=""
        )

        newer_comment = Comment.objects.create(
            id=str(uuid.uuid4()),
            author=self.test_person,
            text="Newer comment",
            created_date=timezone.now(),
            updated_date=timezone.now(),
            likes=0,
            image=""
        )

        response = self.client.get(reverse('get_all_comments'))
        data = response.json()

        self.assertEqual(len(data['comments']), 3)
        self.assertEqual(data['comments'][0]['text'], "Newer comment")
        self.assertIn("Older comment", [c['text'] for c in data['comments']])

    def test_upsert_comment_create_minimal(self):
        """Test creating a new comment with minimal required fields"""
        payload = {
            "text": "New comment text"
        }

        initial_count = Comment.objects.count()

        response = self.client.post(
            reverse('upsert_comment'),
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn('id', data)
        self.assertEqual(data['text'], "New comment text")
        self.assertEqual(data['author']['name'], "Admin")
        self.assertEqual(data['image'], "")

        self.assertEqual(Comment.objects.count(), initial_count + 1)

    def test_upsert_comment_create_with_image(self):
        """Test creating a new comment with optional image field"""
        payload = {
            "text": "Comment with image",
            "image": "https://example.com/new_image.png"
        }

        response = self.client.post(
            reverse('upsert_comment'),
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data['text'], "Comment with image")
        self.assertEqual(data['image'], "https://example.com/new_image.png")

    def test_upsert_comment_create_missing_text(self):
        """Test that creating a comment without text returns error"""
        payload = {}

        response = self.client.post(
            reverse('upsert_comment'),
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], "text is required")

    def test_upsert_comment_update_existing(self):
        """Test updating an existing comment"""
        payload = {
            "comment_id": self.existing_comment.id,
            "text": "Updated comment text"
        }

        initial_count = Comment.objects.count()

        response = self.client.post(
            reverse('upsert_comment'),
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data['id'], self.existing_comment.id)
        self.assertEqual(data['text'], "Updated comment text")

        self.assertEqual(Comment.objects.count(), initial_count)

        self.existing_comment.refresh_from_db()
        self.assertEqual(self.existing_comment.text, "Updated comment text")

    def test_upsert_comment_update_with_image(self):
        """Test updating an existing comment including image field"""
        payload = {
            "comment_id": self.existing_comment.id,
            "text": "Updated with new image",
            "image": "https://example.com/updated_image.jpg"
        }

        response = self.client.post(
            reverse('upsert_comment'),
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data['text'], "Updated with new image")
        self.assertEqual(data['image'], "https://example.com/updated_image.jpg")

        self.existing_comment.refresh_from_db()
        self.assertEqual(self.existing_comment.image, "https://example.com/updated_image.jpg")

    def test_upsert_comment_update_nonexistent(self):
        """Test updating a comment that doesn't exist returns 404"""
        fake_id = str(uuid.uuid4())
        payload = {
            "comment_id": fake_id,
            "text": "This should fail"
        }

        response = self.client.post(
            reverse('upsert_comment'),
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_comment_existing(self):
        """Test deleting an existing comment"""
        comment_id = self.existing_comment.id
        initial_count = Comment.objects.count()

        response = self.client.post(
            reverse('delete_comment', kwargs={'comment_id': comment_id})
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn('message', data)
        self.assertIn(comment_id, data['message'])

        self.assertEqual(Comment.objects.count(), initial_count - 1)
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())

    def test_delete_comment_nonexistent(self):
        """Test deleting a comment that doesn't exist returns 404"""
        fake_id = str(uuid.uuid4())

        response = self.client.post(
            reverse('delete_comment', kwargs={'comment_id': fake_id})
        )

        self.assertEqual(response.status_code, 404)

    def test_crud_workflow(self):
        """Integration test: create, read, update, delete workflow"""
        create_payload = {
            "text": "Workflow test comment",
            "image": "https://example.com/workflow.jpg"
        }

        create_response = self.client.post(
            reverse('upsert_comment'),
            data=json.dumps(create_payload),
            content_type='application/json'
        )
        self.assertEqual(create_response.status_code, 200)
        created_comment = create_response.json()
        comment_id = created_comment['id']

        get_response = self.client.get(reverse('get_all_comments'))
        self.assertEqual(get_response.status_code, 200)
        comments = get_response.json()['comments']
        self.assertTrue(any(c['id'] == comment_id for c in comments))

        update_payload = {
            "comment_id": comment_id,
            "text": "Updated workflow comment"
        }
        update_response = self.client.post(
            reverse('upsert_comment'),
            data=json.dumps(update_payload),
            content_type='application/json'
        )
        self.assertEqual(update_response.status_code, 200)
        updated_comment = update_response.json()
        self.assertEqual(updated_comment['text'], "Updated workflow comment")

        delete_response = self.client.post(
            reverse('delete_comment', kwargs={'comment_id': comment_id})
        )
        self.assertEqual(delete_response.status_code, 200)

        self.assertFalse(Comment.objects.filter(id=comment_id).exists())
