from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Article, Newsletter

# -----------------------------------------------------------------------------
# Custom User Creation Form
# -----------------------------------------------------------------------------
class CustomUserCreationForm(UserCreationForm):
    """
    A form for registering new users with role selection.
    Extends Django's built-in UserCreationForm and adds support for custom fields.
    """

    ROLE_CHOICES = (
        ('Reader', 'Reader'),
        ('Editor', 'Editor'),
        ('Journalist', 'Journalist'),
        ('test', 'test'),  # Temporary or test role
    )
    # Uncomment the line below if you want users to manually select their role.
    # role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'password1', 'password2')


# -----------------------------------------------------------------------------
# Article Management Form
# -----------------------------------------------------------------------------
class ArticleForm(forms.ModelForm):
    """
    Form for creating or updating articles.
    Includes fields for title, content, and selecting the publisher (journalist).
    """

    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']


# -----------------------------------------------------------------------------
# Newsletter Management Form
# -----------------------------------------------------------------------------
class NewsletterForm(forms.ModelForm):
    """
    Form for creating newsletters.
    Includes title, content, and publisher (journalist or approved user).
    """

    class Meta:
        model = Newsletter
        fields = ['title', 'content', 'publisher']


# -----------------------------------------------------------------------------
# Reader Subscription Form
# -----------------------------------------------------------------------------
class SubscriptionForm(forms.ModelForm):
    """
    Form used by readers to manage their subscriptions.
    Allows selection of publishers and journalists to follow.
    """

    class Meta:
        model = CustomUser
        fields = ['subscribed_publishers', 'subscribed_journalists']
        widgets = {
            'subscribed_publishers': forms.CheckboxSelectMultiple,
            'subscribed_journalists': forms.CheckboxSelectMultiple,
        }
