from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


def register_view(request):
  form = UserCreationForm(request.POST or None)

  if request.method == "POST":
    if form.is_valid():
      form.save()
      return redirect('users:login')

  return render(request, 'users/pages/register.html', {'form': form})


def login_view(request):
  form = AuthenticationForm(data=request.POST or None)

  if request.method == "POST":
    if form.is_valid():
      login(request, form.get_user())
      next_url = request.GET.get('next', settings.DEFAULT_LOGIN_REDIRECT_URL)
      return redirect(next_url)

  return render(request, 'users/pages/login.html', {'form': form})

@require_POST
def logout_view(request):
  logout(request)
  return redirect("shop:home_page")


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/pages/profile.html'