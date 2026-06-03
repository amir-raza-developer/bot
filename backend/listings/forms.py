from django import forms
from .models import Listing, AutomationCredential

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "price", "category", "condition", "location", "tags", "images"]

class CredentialForm(forms.ModelForm):
    class Meta:
        model = AutomationCredential
        fields = ["platform", "username", "password"]
