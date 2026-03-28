from django.db import models
from django.conf import settings
from apps.services.models import Doctor  
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'patient')  # one review per patient

    def __str__(self):
        return f"{self.patient} → {self.doctor} ({self.rating}⭐)"
    
@property
def average_rating(self):
    reviews = self.reviews.all()
    if reviews.exists():
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)
    return 0