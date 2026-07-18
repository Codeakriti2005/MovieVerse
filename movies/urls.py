from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("movie/<int:id>/", views.movie_detail, name="movie_detail"),

    path("shows/<int:movie_id>/", views.show_list, name="shows"),

    path("book/<int:show_id>/", views.book_ticket, name="book"),

    path("checkout/", views.checkout, name="checkout"),

    path("payment/", views.payment, name="payment"),

    path("success/", views.success, name="success"),

    path("ticket/<int:booking_id>/", views.download_ticket, name="download_ticket"),

    path("bookings/", views.booking_history, name="booking_history"),

    path("cancel-booking/<int:booking_id>/",views.cancel_booking,name="cancel_booking"),

    path("bookings/", views.booking_history, name="booking_history"),

    path("cancel-booking/<int:booking_id>/",views.cancel_booking,name="cancel_booking"),

    path("wishlist/", views.wishlist,name="wishlist"),

    path("wishlist/add/<int:movie_id>/",views.add_to_wishlist,name="add_to_wishlist"),

    path("wishlist/remove/<int:movie_id>/", views.remove_from_wishlist, name="remove_from_wishlist"),

# ================= Authentication =================

    path("register/", views.register, name="register"),

    # ================= Authentication =================

    path("register/", views.register, name="register"),

    path("login/", views.login_user, name="login"),

    path("logout/", views.logout_user, name="logout"),

    path("profile/", views.profile, name="profile"),

    
]