from django.db import models


class Document(models.Model):
    """
    Represents a cralwed document.
    """

    DOCUMENT_TYPES = [
        ("book", "Book"),
        ("youtube", "Youtube Transcript"),
        ("audio", "Audio Transcript"),
    ]

    url = models.URLField(unique=True, db_index=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField()
    lang = models.CharField(max_length=30, blank=True, null=True, db_index=True)
    document_type = models.CharField(
        max_length=30, choices=DOCUMENT_TYPES, default="book"
    )
    author_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    # For postprocessing
    text_revised = models.TextField(blank=True, null=True)
    is_review_finished = models.BooleanField(default=False)

    def __str__(self):
        return self.title
