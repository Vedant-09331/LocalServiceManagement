from django import forms
from .models import Vendor


class VendorRegisterForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['service', 'phone', 'experience', 'profile_image']


class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['phone', 'experience', 'profile_image', 'bio', 'is_available']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'experience': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years of experience'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell customers about yourself...'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }