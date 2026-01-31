from django.db import models


class Confession(models.Model):
    body = models.CharField(max_length=280, verbose_name="Ta radinerie")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Compteurs de votes
    votes_genie = models.PositiveIntegerField(default=0)
    votes_rat = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.body[:50]
