from django import forms
from django.forms.widgets import TextInput
from month.forms import MonthField

from .models import App, Version, SemanticVersion


class AppForm(forms.ModelForm):
    class Meta:
        model = App
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }


class VersionModelForm(forms.ModelForm):
    changelog = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Version
        fields = ['pub_date', 'name', 'semantic_version', 'changelog', ]


class AddVersionModelForm(forms.ModelForm):
    app = forms.ModelChoiceField(
        label='App',
        queryset=App.objects.order_by('id'),
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )
    name = forms.CharField(
        label='Name',
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    semantic_version = forms.ChoiceField(
        label='Semantic version',
        choices=SemanticVersion.choices,
        widget=forms.Select(
            attrs={'class': 'form-control'},
        )
    )
    pub_date = forms.DateField(
        label='Date published',
        widget=forms.DateInput(
            attrs={'class': 'form-control'}
        )
    )
    changelog = forms.CharField(
        label='Changelog',
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        )
    )

    class Meta:
        model = Version
        fields = '__all__'


class AddRatingsForm(forms.Form):
    date = forms.DateField(
        label='date published',
        widget=forms.DateInput(
            attrs={'class': 'form-control'}
        )
    )
    myf_android = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    myf_ios = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    fon_android = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    fon_ios = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    wlan_android = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    wlan_ios = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    tv_android = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    tv_ios = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    smart_home_android = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    smart_home_ios = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )


class AddActiveUsersForm(forms.Form):
    date = MonthField(
        label='date'
    )
    myf_android = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    myf_ios = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    fon_android = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    fon_ios = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    wlan_android = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    wlan_ios = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    tv_android = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    tv_ios = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    smart_home_android = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    smart_home_ios = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
