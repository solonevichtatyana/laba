from django import forms


class RadioForm(forms.Form):
    wiki = forms.ChoiceField(widget=forms.RadioSelect, choices=((1, 'Enabled'), (0, 'Disabled')))
    crawler_global_search = forms.ChoiceField(widget=forms.RadioSelect, choices=((1, 'Enabled'), (0, 'Disabled')))


class CleanDataBaseForm(forms.Form):
    clear_database = forms.MultipleChoiceField(choices=(('index', 'Index'), ('wiki', 'Wiki Results'),),
                                               widget=forms.CheckboxSelectMultiple())
