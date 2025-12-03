import json
import logging
import uuid

from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from api.models import Comment, Person

logger = logging.getLogger(__name__)


def fetch_current_user() -> Person:
    # TODO- replace this with real auth
    return Person.objects.get(name="Admin")


@csrf_exempt
def get_all_comments(request: HttpRequest) -> JsonResponse:
    comments = Comment.objects.select_related('author').order_by("-created_date")
    
    return JsonResponse({
        "comments": [
            comment.to_dict()
            for comment in comments
        ]
    })


@csrf_exempt
def upsert_comment(request: HttpRequest) -> JsonResponse:
    body = json.loads(request.body)
    
    author = fetch_current_user()
    
    text = body.get("text")
    if not text:
        return JsonResponse({"error": "text is required"}, status=400)
    
    comment_id = body.get("comment_id")
    if comment_id:
        comment = get_object_or_404(Comment, pk=comment_id)
        comment.text = text
        updated_date = timezone.now(),
        comment.image = body.get("image", "")
        comment.save()
    else:
        comment = Comment.objects.create(
            id=uuid.uuid4(),
            created_date=timezone.now(),
            updated_date=timezone.now(),
            author=author,
            text=text,
            image=body.get("image", "")
        )
    
    return JsonResponse(comment.to_dict())


@csrf_exempt
def delete_comment(request: HttpRequest, comment_id: str) -> JsonResponse:
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.delete()
    
    return JsonResponse({
        "message": f"Comment {comment_id} deleted successfully"
    }, status=200)
