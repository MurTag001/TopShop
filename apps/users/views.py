from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.views.generic.list import MultipleObjectMixin
from users.forms import CustomAuthenticationForm

User = get_user_model()


class RegisterView(CreateView):
  template_name = 'users/pages/register.html'
  form_class = UserCreationForm
  success_url = reverse_lazy('users:login')


class LoginView(AuthLoginView):
    template_name = 'users/pages/login.html'
    authentication_form = CustomAuthenticationForm


    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if not next_url:
            return reverse_lazy('users:profile', kwargs={'username': self.request.user.username})

        return next_url
  

class LogoutView(AuthLogoutView):
  next_page = reverse_lazy('shop:home_page')


class ProfileView(DetailView, MultipleObjectMixin):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'users/pages/profile.html'
    context_object_name = 'profile_user'
    paginate_by = 21


    def get_context_data(self, **kwargs):
        products = self.object.products.all()
        context = super().get_context_data(object_list=products, **kwargs)
        context['products_list'] = context['object_list']

        del context['object_list']
        
        return context