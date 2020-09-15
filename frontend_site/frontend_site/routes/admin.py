from django import forms
from django.contrib import admin

from .models import Route


class RouteForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size': '40'}))
    path = forms.CharField(widget=forms.TextInput(attrs={'size': '80'}), required=False)
    endpoint = forms.CharField(widget=forms.TextInput(attrs={'size': '80'}), required=False)
    template_name = forms.CharField(widget=forms.TextInput(attrs={'size': '40'}))
    content_type = forms.CharField(widget=forms.TextInput(attrs={'size': '40'}))

    class Meta:
        model = Route
        fields = '__all__'


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    form = RouteForm

    list_display = ['id', 'order', 'name', 'path', 'endpoint', 'template_name', 'content_type']
    list_editable = ['order']
    ordering = ['order']
