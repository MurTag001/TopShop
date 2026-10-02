from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST


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
      return redirect("shop:home_page")

  return render(request, 'users/pages/login.html', {'form': form})

@require_POST
def logout_view(request):
  logout(request)
  return redirect("shop:home_page")