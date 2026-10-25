from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import F, Q, Exists, OuterRef
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import ProductForm
from .models import Category, Manufacturer, Product, Tag


class HomePageView(TemplateView):
    template_name = "shop/pages/index.html"


class ProductListView(ListView):
    queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('tags')
    context_object_name = "products"
    template_name = "shop/pages/product_list.html"
    paginate_by = 21

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_products = context["products"]
        
        user = self.request.user
        if user.is_authenticated:
            viewed_ids = set(user.viewed_products.values_list('id', flat=True))
            
            for product in page_products:
                product.is_viewed = product.id in viewed_ids
                
        return context


class ShopDetailView(DetailView):
    slug_url_kwarg = "product_slug"
    template_name = "shop/pages/product_detail.html"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Product.objects.filter(
                Q(is_active=True) | Q(owner=self.request.user)
            )
        return Product.objects.filter(is_active=True)

    def get_object(self, queryset=None):
        product = super().get_object(queryset)
        user = self.request.user

        session_key = f'product_{product.id}_viewed'
        if not self.request.session.get(session_key, False) and product.owner != user:
            Product.objects.filter(id=product.id).update(views=F("views") + 1)
            product.views += 1
            self.request.session[session_key] = True

        if user.is_authenticated and user != product.owner:
            product.viewed_by_users.add(user)

        return product


class CategoryProductsView(ListView):
    context_object_name = "products"
    template_name = "shop/pages/category_products.html"
    paginate_by = 21

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"]
        )
        return self.category.products.filter(is_active=True).select_related('category', 'manufacturer', 'owner').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class TagProductsView(ListView):
    context_object_name = "products"
    template_name = "shop/pages/tag_products.html"
    paginate_by = 21

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["tag_slug"])
        return self.tag.products.filter(is_active=True).select_related('category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        
        page_products = context["products"]
        user = self.request.user
        if user.is_authenticated:
            viewed_ids = set(user.viewed_products.values_list('id', flat=True))
            for product in page_products:
                product.is_viewed = product.id in viewed_ids
                
        return context


class ProductsSearchView(ListView):
    model = Product
    template_name = "shop/pages/products_search.html"
    context_object_name = 'products'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_performed'] = bool(self.request.GET.get("q"))
        return context

    def get_queryset(self):
        search_query = self.request.GET.get("q")
        if search_query:
            queryset = Product.objects.filter(is_active=True)
            condition = Q(name__icontains=search_query) | Q(description__icontains=search_query)
            search_in_categories = self.request.GET.get("in_categories") == 'on'
            search_in_tags = self.request.GET.get("in_tags") == 'on'
            search_in_manufacturer = self.request.GET.get("in_manufacturer") == 'on'
            if search_in_categories:
                condition |= Q(category__name__icontains=search_query)
            if search_in_tags:
                condition |= Q(tags__name__icontains=search_query)
            if search_in_manufacturer:
                condition |= Q(manufacturer__name__icontains=search_query)
            return queryset.filter(condition).distinct()
        return Product.objects.none()

    
class ManufacturerProductsView(ListView):
    template_name = "shop/pages/manufacturer_products.html"
    context_object_name = "products"
    paginate_by = 21

    def dispatch(self, request, *args, **kwargs):
        self.manufacturer = get_object_or_404(
            Manufacturer, 
            slug=self.kwargs["manufacturer_slug"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.manufacturer.products.filter(
            is_active=True
        ).select_related('category').prefetch_related('tags')

        if self.request.user.is_authenticated:
            is_viewed_subquery = Product.viewed_by_users.through.objects.filter(
                product_id=OuterRef('pk'),
                user_id=self.request.user.id
            )
            queryset = queryset.annotate(is_viewed=Exists(is_viewed_subquery))
            
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["manufacturer"] = self.manufacturer
        return context


class ProductAddView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "shop/pages/product_add.html"

    def form_valid(self, form):
        product = form.save(commit=False)
        product.owner = self.request.user

        m_name = form.cleaned_data.get("manufacturer_input")
        m_country = form.cleaned_data.get("manufacturer_country_input") or "Не указана"

        if m_name and m_name.strip():
            m_name = m_name.strip().title()
            manufacturer, created = Manufacturer.objects.get_or_create(
                name=m_name,
                defaults={
                    "country": m_country,
                    "description": f"Производитель {m_name}",
                },
            )
            product.manufacturer = manufacturer
        else:
            product.manufacturer = None

        product.save()

        tag_names = form.cleaned_data.get("tags_input") or []
        for tag_name in tag_names:
            if tag_name.strip():
                normalized_tag = tag_name.strip().lower()
                tag, _ = Tag.objects.get_or_create(name=normalized_tag)
                product.tags.add(tag)

        form.save_m2m()
        self.object = product
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "shop:product_detail", kwargs={"product_slug": self.object.slug}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Добавить позицию",
                "h1": "Новый товар",
                "submit_button_text": "Добавить",
            }
        )
        return context


class ProductEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "shop/pages/product_form.html"
    slug_url_kwarg = "product_slug"
    _cached_object = None

    def get_object(self, queryset=None):
        if self._cached_object is None:
            if queryset is None:
                queryset = self.get_queryset()

            product_slug = self.kwargs.get(self.slug_url_kwarg)
            condition = Q(slug=product_slug) & (
                Q(is_active=True) | Q(owner=self.request.user)
            )
            self._cached_object = get_object_or_404(queryset, condition)

        return self._cached_object

    def test_func(self):
        product = self.get_object()
        return self.request.user == product.owner

    def handle_no_permission(self):
        return render(self.request, "shop/pages/not_allowed.html")

    def get_initial(self):
        initial = super().get_initial()
        product = self.get_object()

        if product.manufacturer:
            initial["manufacturer_input"] = product.manufacturer.name
            initial["manufacturer_country_input"] = product.manufacturer.country

        initial["tags_input"] = ", ".join(tag.name for tag in product.tags.all())
        return initial

    def form_valid(self, form):
        product = form.save(commit=False)

        m_name = form.cleaned_data.get("manufacturer_input")
        m_country = form.cleaned_data.get("manufacturer_country_input") or "Не указана"

        if m_name and m_name.strip():
            m_name = m_name.strip().title()
            manufacturer, _ = Manufacturer.objects.get_or_create(
                name=m_name, 
                defaults={"country": m_country}
            )
            product.manufacturer = manufacturer
        else:
            product.manufacturer = None

        product.save()

        product.tags.clear()
        tag_names = form.cleaned_data.get("tags_input") or []
        for tag_name in tag_names:
            if tag_name.strip():
                normalized_tag = tag_name.strip().lower()
                tag, _ = Tag.objects.get_or_create(name=normalized_tag)
                product.tags.add(tag)

        form.save_m2m()
        self.object = product
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "shop:product_detail", kwargs={"product_slug": self.object.slug}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Редактировать позицию",
                "h1": "Редактирование",
                "submit_button_text": "Сохранить",
            }
        )
        return context


class ProductRemoveView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = "shop/pages/product_remove_confirm.html"
    slug_url_kwarg = "product_slug"
    context_object_name = "product"
    success_url = reverse_lazy("shop:product_list")

    def test_func(self):
        product = self.get_object()
        return self.request.user == product.owner

    def handle_no_permission(self):
        return render(self.request, "shop/pages/not_allowed.html")