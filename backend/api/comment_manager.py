import json
import logging
from pathlib import Path

from django.utils import timezone

from api.models import Comment, Person


def import_comments(comment_file: Path, reset=False):
    comment_file = Path(comment_file)
    if not comment_file.exists():
        raise ValueError(f"{comment_file} does not exist")
    
    if reset:
        logging.info(f"Deleting all existing comments")
        Comment.objects.all().delete()
    
    comment_file_contents = json.loads(comment_file.read_text())
    comment_datas = comment_file_contents.get("comments")
    if not comment_datas:
        raise ValueError(f"no comments found in {comment_file}")
    
    logging.info(f"Ingesting {len(comment_datas)} from {comment_file}")
    authors = {
        comment_data.get("author")
        for comment_data in comment_datas
    }
    authors.add("Admin")
    
    author_id_map = {}
    for author in authors:
        p, _ = Person.objects.update_or_create(
            name=author
        )
        author_id_map[p.name] = p.id
    
    for comment_data in comment_datas:
        Comment.objects.update_or_create(
            id=comment_data.get("id"),
            defaults={
                "author_id": author_id_map.get(comment_data.get("author")),
                "text": comment_data.get("text"),
                "created_date": comment_data.get("date"),
                "updated_date": timezone.now(),
                "likes": comment_data.get("likes"),
                "image": comment_data.get("image")
            }
        )
    logging.info(f"Have {Comment.objects.count()} after ingesting {comment_file}")


