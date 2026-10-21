from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify
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
    queryset = Product.objects.filter(is_active=True)
    context_object_name = "products"
    template_name = "shop/pages/product_list.html"
    paginate_by = 10


class ShopDetailView(DetailView):
    slug_url_kwarg = "product_slug"
    template_name = "shop/pages/product_detail.html"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Product.objects.filter(
                Q(is_active=True) | Q(owner=self.request.user)
            )
        return Product.objects.filter(is_active=True)


class CategoryProductsView(ListView):
    context_object_name = "products"
    template_name = "shop/pages/category_products.html"

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"]
        )
        return self.category.products.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class TagProductsView(ListView):
    context_object_name = "products"
    template_name = "shop/pages/tag_products.html"

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["tag_slug"])
        return self.tag.products.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        return context


class ManufacturerProductsView(ListView):
    template_name = "shop/pages/manufacturer_products.html"
    context_object_name = "products"

    def get_queryset(self):
        self.manufacturer = get_object_or_404(
            Manufacturer, slug=self.kwargs["manufacturer_slug"]
        )
        return self.manufacturer.products.filter(is_active=True)

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
        m_country = (
            form.cleaned_data.get("manufacturer_country_input") or "Не указана"
        )

        if m_name and m_name.strip():
            m_name = m_name.strip()
            m_slug = (
                slugify(m_name.lower(), allow_unicode=True)
                or "manufacturer-slug"
            )

            manufacturer, created = Manufacturer.objects.get_or_create(
                name=m_name,
                defaults={
                    "country": m_country,
                    "slug": m_slug,
                    "description": f"Производитель {m_name}",
                },
            )
            product.manufacturer = manufacturer
        else:
            product.manufacturer = None

        product.save()

        tag_names = form.cleaned_data.get("tags_input") or []
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
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
            initial["manufacturer_country_input"] = (
                product.manufacturer.country
            )

        initial["tags_input"] = ", ".join(tag.name for tag in product.tags.all())
        return initial

    def form_valid(self, form):
        product = form.save(commit=False)

        m_name = form.cleaned_data.get("manufacturer_input")
        m_country = (
            form.cleaned_data.get("manufacturer_country_input") or "Не указана"
        )

        if m_name and m_name.strip():
            m_name = m_name.strip()
            m_slug = (
                slugify(m_name.lower(), allow_unicode=True)
                or "manufacturer-slug"
            )

            manufacturer, _ = Manufacturer.objects.get_or_create(
                name=m_name, defaults={"country": m_country, "slug": m_slug}
            )
            product.manufacturer = manufacturer
        else:
            product.manufacturer = None

        product.save()

        product.tags.clear()
        tag_names = form.cleaned_data.get("tags_input") or []
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
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