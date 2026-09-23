from django import forms
from .models import ProductBookCategory


from django import forms
from .models import ProductBookCategory


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