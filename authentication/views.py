from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import UserSession


@login_required
def user_sessions(request):
    """
    Display active sessions for the current user.
    """
    active_sessions = UserSession.objects.filter(
        user=request.user, is_active=True
    ).order_by("-last_activity")

    # Get current session key for highlighting
    current_session_key = request.session.session_key

    context = {
        "active_sessions": active_sessions,
        "current_session_key": current_session_key,
    }
    return render(request, "authentication/user_sessions.html", context)


@login_required
@require_POST
def terminate_session(request, session_id):
    """
    Terminate a specific user session.
    """
    user_session = get_object_or_404(
        UserSession, id=session_id, user=request.user, is_active=True
    )

    # Don't allow terminating current session via this method
    if user_session.session.session_key == request.session.session_key:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": False,
                    "message": "Cannot terminate current session. Please logout instead.",
                }
            )
        messages.error(
            request, "Cannot terminate current session. Please logout instead."
        )
        return redirect("authentication:user_sessions")

    try:
        user_session.terminate_session()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": True, "message": "Session terminated successfully."}
            )
        messages.success(request, "Session terminated successfully.")
    except Exception as e:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": False, "message": f"Error terminating session: {str(e)}"}
            )
        messages.error(request, f"Error terminating session: {str(e)}")

    return redirect("authentication:user_sessions")


@login_required
@require_POST
def terminate_all_sessions(request):
    """
    Terminate all sessions except the current one.
    """
    current_session_key = request.session.session_key

    sessions_to_terminate = UserSession.objects.filter(
        user=request.user, is_active=True
    ).exclude(session__session_key=current_session_key)

    count = 0
    for user_session in sessions_to_terminate:
        try:
            user_session.terminate_session()
            count += 1
        except Exception:
            continue

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {"success": True, "message": f"{count} sessions terminated successfully."}
        )

    messages.success(request, f"{count} other sessions have been terminated.")
    return redirect("authentication:user_sessions")


def session_security_info(request):
    """
    Display information about session security features.
    """
    return render(request, "authentication/session_security_info.html")
