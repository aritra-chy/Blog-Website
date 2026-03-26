from .models import Profile


def navbar_profile(request):
    if not request.user.is_authenticated:
        return {"navbar_profile": None}

    profile = Profile.objects.filter(user=request.user).first()
    return {"navbar_profile": profile}