from django import forms

class MessageRetrievalForm(forms.Form):
    num_messages = forms.IntegerField(max_value=5000)