from django.contrib import admin
from .models import Movie, Show, Booking, Cast


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "genre",
        "language",
        "rating",
        "release",
    )

    search_fields = (
        "title",
        "genre",
        "language",
    )


@admin.register(Cast)
class CastAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "movie",
        "role",
    )

    search_fields = (
        "name",
        "movie__title",
    )


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = (
        "movie",
        "show_time",
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "customer_name",
        "movie",
        "email",
        "booked_at",
    )

    search_fields = (
        "customer_name",
        "movie__title",
    )