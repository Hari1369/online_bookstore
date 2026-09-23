from django import forms
from .models import ProductBookCategory


from django import forms
from .models import ProductBookCategory, ProductBookDetails


class ProductBookCategoryForm(forms.ModelForm):

    class Meta:
        model = ProductBookCategory
        fields = ["choice"]
        widgets = {
            "choice": forms.TextInput(attrs={
                "placeholder": "Enter book category",
                "class": "category-input"
            })
        }

    def clean_choice(self):
        choice = self.cleaned_data["choice"].strip()
        if not choice:
            raise forms.ValidationError(
                "Category cannot be empty."
            )

        return choice


class BookCategoryCSVForm(forms.Form):
    csv_file = forms.FileField(
        label="Upload CSV",
        required=True
    )
    def clean_csv_file(self):
        csv_file = self.cleaned_data["csv_file"]

        if not csv_file.name.endswith(".csv"):
            raise forms.ValidationError(
                "Please upload a CSV file."
            )

        return csv_file

class ProductBookDetailsForm(forms.ModelForm):
    class Meta:
        model = ProductBookDetails
        fields = [
            "isbn",
            "title",
            "author",
            "description",
            "category",
            "price",
            "publication_year",
            "image",
            "pdf",
            "total_copies",
            "available_copies",
            "is_active",
        ]

        widgets = {
            "isbn": forms.TextInput(attrs={
                "placeholder": "Enter ISBN",
                "class": "book-input"
            }),

            "title": forms.TextInput(attrs={
                "placeholder": "Enter book title",
                "class": "book-input"
            }),

            "author": forms.TextInput(attrs={
                "placeholder": "Enter author name",
                "class": "book-input"
            }),

            "description": forms.Textarea(attrs={
                "placeholder": "Enter book description",
                "class": "book-input",
                "rows": 5
            }),

            "category": forms.Select(attrs={
                "class": "book-input"
            }),

            "price": forms.NumberInput(attrs={
                "placeholder": "Enter price",
                "class": "book-input",
                "step": "0.01"
            }),

            "publication_year": forms.NumberInput(attrs={
                "placeholder": "Enter publication year",
                "class": "book-input"
            }),

            "image": forms.ClearableFileInput(attrs={
                "class": "book-input"
            }),

            "pdf": forms.ClearableFileInput(attrs={
                "class": "book-input",
                "accept": ".pdf"
            }),

            "total_copies": forms.NumberInput(attrs={
                "placeholder": "Enter total copies",
                "class": "book-input",
                "min": "0"
            }),

            "available_copies": forms.NumberInput(attrs={
                "placeholder": "Enter available copies",
                "class": "book-input",
                "min": "0"
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "book-checkbox"
            }),
        }

    def clean_available_copies(self):
        available = self.cleaned_data["available_copies"]
        total = self.cleaned_data.get("total_copies")
        if total is not None and available > total:
            raise forms.ValidationError("Available copies cannot be greater than total copies")
        return available

    def clean_pdf(self):
        pdf = self.cleaned_data.get("pdf")
        if pdf:
            if not pdf.name.lower().endswith(".pdf"):
                raise forms.ValidationError("Only PDF files are allowed!")
        return pdf