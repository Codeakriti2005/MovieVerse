from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie, Booking, Cast, Wishlist, Review
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import random
import datetime
import qrcode
import os
from django.conf import settings
from reportlab.pdfgen import canvas
from django.http import HttpResponse

# ===========================
# HOME
# ===========================

def home(request):

    query = request.GET.get("q")

    if query:
        movies = Movie.objects.filter(title__icontains=query)
    else:
        movies = Movie.objects.all()

    return render(request, "home.html", {
        "movies": movies,
        "query": query,
    })


# ===========================
# MOVIE DETAIL
# ===========================

def movie_detail(request, id):

    movie = get_object_or_404(Movie, id=id)

    casts = Cast.objects.filter(movie=movie)

    reviews = Review.objects.filter(movie=movie).order_by("-created_at")

    if request.method == "POST":

        if request.user.is_authenticated:

            rating = request.POST.get("rating")

            comment = request.POST.get("comment")

            Review.objects.create(
                movie=movie,
                user=request.user,
                rating=rating,
                comment=comment
            )

            messages.success(request, "Review Added Successfully ⭐")

            return redirect("movie_detail", id=movie.id)

        else:

            return redirect("login")

    return render(request, "movie_detail.html", {
        "movie": movie,
        "casts": casts,
        "reviews": reviews,
    })


# ===========================
# SHOW LIST
# ===========================

def show_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    shows = [
        {"id": movie.id, "time": "10:00 AM"},
        {"id": movie.id, "time": "1:00 PM"},
        {"id": movie.id, "time": "4:00 PM"},
        {"id": movie.id, "time": "7:30 PM"},
    ]

    return render(request, "shows.html", {
        "movie": movie,
        "shows": shows,
    })


# ===========================
# BOOK TICKET
# ===========================

@login_required(login_url='login')
def book_ticket(request, show_id):

    movie = get_object_or_404(Movie, id=show_id)

    seats = []

    rows = ["A", "B", "C", "D", "E"]

    for row in rows:
        for num in range(1, 9):
            seats.append(f"{row}{num}")

    bookings = Booking.objects.filter(movie=movie)

    booked_seats = []

    for booking in bookings:
        booked_seats.extend(booking.seats.split(","))

    return render(request, "book.html", {
        "movie": movie,
        "show_id": movie.id,
        "seats": seats,
        "booked_seats": booked_seats,
    })


# ===========================
# CHECKOUT
# ===========================

@login_required(login_url='login')
def checkout(request):

    if request.method == "GET":

        movie_id = request.GET.get("movie_id")
        selected_seats = request.GET.get("selected_seats", "")

        seat_list = [seat for seat in selected_seats.split(",") if seat]

        total_amount = len(seat_list) * 200

        return render(request, "checkout.html", {
            "movie_id": movie_id,
            "selected_seats": selected_seats,
            "total_amount": total_amount,
        })

    if request.method == "POST":

        movie_id = request.POST.get("movie_id")
        seats = request.POST.get("seats")
        total_amount = request.POST.get("total_amount")

        request.session["movie_id"] = movie_id
        request.session["seats"] = seats
        request.session["name"] = request.POST.get("name")
        request.session["email"] = request.POST.get("email")
        request.session["phone"] = request.POST.get("phone")
        request.session["total_amount"] = total_amount

        return redirect("payment")
    

@login_required(login_url='login')
def payment(request):

    if request.method == "POST":

        # ==========================
        # FINAL PAYMENT
        # ==========================
        if "pay_now" in request.POST:

            movie = get_object_or_404(
                Movie,
                id=request.POST.get("movie_id")
            )

            booking = Booking.objects.create(
                user=request.user,
                movie=movie,
                customer_name=request.POST.get("name"),
                email=request.POST.get("email"),
                seats=request.POST.get("seats"),
          )

            payment_id = "PAYMV" + str(random.randint(1000000000, 9999999999))
            booking_id = "MV" + str(booking.id).zfill(5)

            # ==========================
            # QR CODE GENERATION
            # ==========================

            qr_text = f"""
Movie : {movie.title}
Customer : {booking.customer_name}
Booking ID : {booking_id}
Payment ID : {payment_id}
Seats : {booking.seats}
"""

            qr = qrcode.make(qr_text)

            qr_folder = os.path.join(settings.MEDIA_ROOT, "qr")

            os.makedirs(qr_folder, exist_ok=True)

            qr_filename = f"{booking_id}.png"

            qr.save(os.path.join(qr_folder, qr_filename))

            qr_path = "qr/" + qr_filename

            return render(request, "success.html", {

                "movie": movie,
                "booking": booking,
                "payment_id": payment_id,
                "booking_id": booking_id,
                "amount": request.POST.get("total_amount"),
                "seats": booking.seats,
                "qr_path": qr_path,

            })

        # ==========================
        # CHECKOUT → PAYMENT
        # ==========================

        movie = get_object_or_404(
            Movie,
            id=request.POST.get("movie_id")
        )

        return render(request, "payment.html", {

            "movie": movie,
            "movie_id": movie.id,
            "name": request.POST.get("name"),
            "email": request.POST.get("email"),
            "phone": request.POST.get("phone"),
            "seats": request.POST.get("seats"),
            "amount": request.POST.get("total_amount"),

        })

    return redirect("home")

    


# ===========================
# SUCCESS
# ===========================

def success(request):
    return render(request, "success.html")


# ===========================
# BOOKING HISTORY
# ===========================
@login_required(login_url='login')
def booking_history(request):

    bookings = Booking.objects.filter(
        user=request.user
    ).order_by("-booked_at")

    return render(request, "booking_history.html", {
        "bookings": bookings
    })


# ===========================
# REGISTER
# ===========================

def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully!")
        return redirect("login")

    return render(request, "register.html")


# ===========================
# LOGIN
# ===========================

def login_user(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("home")

        messages.error(request, "Invalid Username or Password")

    return render(request, "login.html")


# ===========================
# LOGOUT
# ===========================

def logout_user(request):

    logout(request)
    return redirect("home")


# ===========================
# PROFILE
# ===========================

@login_required(login_url='login')
def profile(request):

    total_bookings = Booking.objects.filter(
        email=request.user.email
    ).count()

    wishlist_count = Wishlist.objects.filter(
        user=request.user
    ).count()

    reviews_count = Review.objects.filter(
        user=request.user
    ).count()

    return render(request, "profile.html", {

        "total_bookings": total_bookings,
        "wishlist_count": wishlist_count,
        "reviews_count": reviews_count,

    })
@login_required(login_url='login')
def download_ticket(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=Ticket_{booking.id}.pdf'

    p = canvas.Canvas(response)

    p.setFont("Helvetica-Bold", 22)
    p.drawString(180, 800, "MovieVerse Ticket")

    p.setFont("Helvetica", 14)

    p.drawString(50, 740, f"Movie : {booking.movie.title}")
    p.drawString(50, 710, f"Customer : {booking.customer_name}")
    p.drawString(50, 680, f"Email : {booking.email}")
    p.drawString(50, 650, f"Seats : {booking.seats}")
    p.drawString(50, 620, f"Booking ID : MV{str(booking.id).zfill(5)}")
    p.drawString(50, 590, f"Booking Date : {booking.booked_at.strftime('%d-%m-%Y %H:%M')}")

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 530, "Status : CONFIRMED")

    p.save()

    return response

@login_required(login_url='login')
def cancel_booking(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    booking.delete()

    messages.success(request, "Booking cancelled successfully!")

    return redirect("booking_history")

@login_required(login_url='login')
def add_to_wishlist(request, movie_id):

    movie = get_object_or_404(Movie, id=movie_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        movie=movie
    )

    messages.success(request, "Movie added to Wishlist ❤️")

    return redirect("home")


@login_required(login_url='login')
def wishlist(request):

    wishlist = Wishlist.objects.filter(
        user=request.user
    )

    return render(request, "wishlist.html", {
        "wishlist": wishlist
    })

@login_required(login_url='login')
def remove_from_wishlist(request, movie_id):

    Wishlist.objects.filter(
        user=request.user,
        movie_id=movie_id
    ).delete()

    messages.success(request, "Movie removed from Wishlist 💔")

    return redirect("wishlist")