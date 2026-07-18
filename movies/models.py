from django.db import models
from django.contrib.auth.models import User


class Movie(models.Model):
    title = models.CharField(max_length=100)
    rating = models.CharField(max_length=20)
    genre = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    language = models.CharField(max_length=100)
    release = models.CharField(max_length=100)
    trailer = models.URLField(blank=True)
    image = models.ImageField(upload_to="movies/")
    about = models.TextField()

    def __str__(self):
        return self.title


class Cast(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="casts"
    )
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    image = models.ImageField(upload_to="cast/")

    def __str__(self):
        return f"{self.name} - {self.movie.title}"


class Show(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    show_time = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.movie.title} - {self.show_time}"

class Booking(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    seats = models.CharField(max_length=100)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.movie.title}"
    


class Wishlist(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE
    )

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"
    
class Review(models.Model):

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"