from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


# -----------------------------------------------------------------------------  
# Publisher Model  
# -----------------------------------------------------------------------------  
class Publisher(models.Model):
    """
    Represents a publishing entity that authors (journalists) can be affiliated with.
    Readers can subscribe to publishers to receive articles/newsletters.
    """
    name = models.CharField(max_length=100)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='publisher_profile',
        null=True,
        blank=True,
        help_text="The journalist user associated with this publisher."
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# -----------------------------------------------------------------------------  
# Custom User Model with Role Support  
# -----------------------------------------------------------------------------  
class CustomUser(AbstractUser):
    """
    Extends Django's built-in User model to include user roles and subscription logic.
    Supports:
        - reader: can subscribe to publishers and journalists
        - editor: can approve or manage articles
        - journalist: can write articles/newsletters
    """
    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        help_text="Defines the user's role: reader, editor, or journalist."
    )

    subscribed_publishers = models.ManyToManyField(
        Publisher,
        blank=True,
        related_name='subscribers',
        help_text="Publishers that the user (as a reader) is subscribed to."
    )

    subscribed_journalists = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='journalist_followers',
        help_text="Journalists that the user (as a reader) is subscribed to."
    )

    updated_at = models.DateTimeField(auto_now=True)

    def publisher(self):
        """
        Returns the Publisher instance linked to this user if journalist.
        """
        return getattr(self, 'publisher_profile', None)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_role = None
        if not is_new:
            old_role = CustomUser.objects.get(pk=self.pk).role
        super().save(*args, **kwargs)

        # Clear subscriptions if role changed to journalist
        if self.role == 'journalist' and old_role != 'journalist':
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()


# -----------------------------------------------------------------------------  
# Article Model  
# -----------------------------------------------------------------------------  
class Article(models.Model):
    """
    Represents a news article written by a journalist and affiliated with a publisher.
    Editors can approve articles before they are published.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    summary = models.CharField(max_length=500, blank=True, null=True)
    approved = models.BooleanField(default=False)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles',
        help_text="User who wrote the article (typically a journalist)."
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='articles',
        help_text="Publisher the article belongs to."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ('can_publish_article', 'Can publish article'),
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"


# -----------------------------------------------------------------------------  
# Newsletter Model  
# -----------------------------------------------------------------------------  
class Newsletter(models.Model):
    """
    Represents a newsletter created by a journalist for a specific publisher.
    Can be used for periodic updates or editorial content.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='newsletters',
        help_text="User who authored the newsletter."
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='newsletters',
        help_text="Publisher the newsletter is associated with."
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ('can_publish_newsletter', 'Can publish newsletter'),
        ]

    def __str__(self):
        return self.title
