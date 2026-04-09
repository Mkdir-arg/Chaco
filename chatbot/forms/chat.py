from django import forms


class SendMessageForm(forms.Form):
    message = forms.CharField()

    def clean_message(self):
        return self.cleaned_data["message"].strip()


class FeedbackForm(forms.Form):
    message_id = forms.IntegerField()
    rating = forms.IntegerField(min_value=1, max_value=5)
    comment = forms.CharField(required=False)


class ApiKeyForm(forms.Form):
    api_key = forms.CharField()

    def clean_api_key(self):
        return self.cleaned_data["api_key"].strip()


class KnowledgeForm(forms.Form):
    title = forms.CharField(max_length=200)
    content = forms.CharField()
    category = forms.CharField(max_length=100)
