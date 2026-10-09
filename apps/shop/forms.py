from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock', 'is_active', 'image']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'id': 'titleInput',
                'placeholder': 'Длина от 6 до 200 символов',
                'minlength': '6',
                'maxlength': '200',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'id': 'textInput',
                'rows': 3,
            }),
            'price': forms.NumberInput(attrs={
                'id': 'priceInput',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
                'required': True
            }),
            'stock': forms.NumberInput(attrs={
                'id': 'stockInput',
                'min': '0',
                'placeholder': '0',
                'required': True
            }),
            'is_active': forms.CheckboxInput(attrs={
                'id': 'activeInput',
                'class': 'form-check-input'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'}),
            'image': forms.FileInput(attrs={
                'class': 'form-control'})
        }
        
        labels = {
            'name': 'Наименование:',
            'category': 'Категория:',
            'description': 'Описание:',
            'price': 'Цена:',
            'stock': 'Количество на складе:',
            'is_active': 'Доступен для продажи',
            'image': 'Картинка товара'
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 6:
            raise forms.ValidationError("Наименование не должно быть короче 6 символов.")
        return name
