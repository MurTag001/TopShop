from django.conf import settings
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from shop.models import Product

User = get_user_model()

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


class ProfileView(DetailView):
    model = User
    template_name = 'users/pages/profile.html'
    context_object_name = 'profile_user'


    def get_object(self, queryset=None):
        username = self.kwargs.get("username")
        return get_object_or_404(User, username=username)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()
        context['products_list'] = Product.objects.filter(owner=profile_user)
        
        return context