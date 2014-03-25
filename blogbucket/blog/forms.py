from django import forms

from django.contrib.auth.models import User
from models import *
from django import forms

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length = 30)
    last_name = forms.CharField(max_length = 30)
    username = forms.CharField(max_length = 20)
    email = forms.EmailField(max_length = 40)
    password1 = forms.CharField(max_length = 200, 
                                label='Password', 
                                widget = forms.PasswordInput())
    password2 = forms.CharField(max_length = 200, 
                                label='Confirm password',  
                                widget = forms.PasswordInput())

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        return username


class BlogsForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 90}), label='New Post')
    class Meta:
        model = Blogs
        exclude = ('user', )
        widgets = {'picture' : forms.FileInput() }
        # fields = ('first_name', 'last_name', ... etc.,)
                           
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'token',  )
        # fields = ('first_name', 'last_name', ... etc.,)
