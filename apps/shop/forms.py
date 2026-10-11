from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
      
    tags_input = forms.CharField(
    required=False,
    widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Введите теги через запятую'
    }),
    label="Теги",
    help_text="- можно указать несколько тегов",
    )

    class Meta:
        model = Product
        fields = ['name', 'category', 'tags_input', 'description', 'price', 'stock', 'is_active', 'image']
        
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
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control'}),
            'image': forms.FileInput(attrs={
                'class': 'form-control'})
        }
        
        labels = {
            'name': 'Наименование:',
            'category': 'Категория:',
            'tags': 'Теги:',
            'description': 'Описание:',
            'price': 'Цена:',
            'stock': 'Количество на складе:',
            'is_active': 'Доступен для продажи',
            'image': 'Картинка товара'
        }
        help_texts = {
      'category': "- можно выбрать только одну категорию",
      'tags': '- можно выбрать несколько тегов',
    }
        

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 6:
            raise forms.ValidationError("Наименование не должно быть короче 6 символов.")
        return name


    def clean_tags_input(self):
        tag_names = [
            tag_name.strip().lower()
            for tag_name in self.cleaned_data.get('tags_input').split(',')
            if tag_name.strip()
        ]
        return tag_names
