import uuid

from django.db import models


class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(db_index=True)


class Comment(models.Model):
    id = models.TextField(primary_key=True)
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField()
    likes = models.IntegerField(default=0)
    image = models.URLField(max_length=500, blank=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "author": {
                "id": str(self.author.id),
                "name": self.author.name
            },
            "text": self.text,
            "created_date": self.created_date.isoformat(),
            "updated_date": self.updated_date.isoformat(),
            "likes": self.likes,
            "image": self.image
        }
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.author_id}: {self.text[:50]}..."
