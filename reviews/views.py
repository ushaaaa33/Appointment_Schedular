from reviews.models import Review, Doctor
from django.shortcuts import get_object_or_404, redirect, render

def doctor_profile(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)

    has_reviewed = False
    if request.user.is_authenticated:
        has_reviewed = Review.objects.filter(
            doctor=doctor,
            patient=request.user
        ).exists()

    if request.method == "POST":
        if request.user.is_authenticated:
            rating = request.POST.get("rating")
            comment = request.POST.get("comment")

            if rating:
                Review.objects.update_or_create(
                    doctor=doctor,
                    patient=request.user,
                    defaults={
                        "rating": rating,
                        "comment": comment
                    }
                )
        return redirect("doctor_profile", pk=pk)

    return render(request, "doctor/doctor_profile.html", {
        "doctor": doctor,
        "has_reviewed": has_reviewed
    })
