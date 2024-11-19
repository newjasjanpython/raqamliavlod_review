from datetime import timedelta, datetime
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from .models import Masala

MAX_TIME = timedelta(hours=15)

def check_contest_time(fn):
    def wrapper(request, *args, **kwargs):
        if request.method == "POST":
            masala = get_object_or_404(Masala, id=kwargs.get('masala_id'))
            current_time = now()

            user_contests = request.user.kontests.all()
            for contest in user_contests:
                if masala in contest.kontest.masalalar.all():
                    if contest.created_at:
                        time_difference = current_time - contest.created_at
                        if time_difference > MAX_TIME:
                            messages.add_message(request, messages.ERROR, "Sizga test yechish uchun berilgan vaqt tugadi.")

                            return redirect(request.path)
                    else:
                        contest.created_at = now()
                        contest.save()
                    break

        return fn(request, *args, **kwargs)

    return wrapper
