from django.core.management.base import BaseCommand

from api import comment_manager


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--comment_file',
            type=str,
            default="../data/comments.json",
            required=False
        )
        
        parser.add_argument(
            '--reset',
            action="store_true"
        )
    
    def handle(self, *args, **options):
        comment_manager.import_comments(
            options.get("comment_file"),
            options.get("reset")
        )
