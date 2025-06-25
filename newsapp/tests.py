from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from newsapp.models import Journalist, Publisher, Newsletter

User = get_user_model()


class NewsletterCreateTest(TestCase):
    """
    Test case for verifying that a journalist can successfully create a newsletter.
    """

    def setUp(self):
        """
        Set up test data:
        - Create a Publisher instance.
        - Create a User who will act as a journalist.
        - Create a Journalist linked to the User and Publisher.
        """
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.user = User.objects.create_user(username="journalist", password="testpass")
        self.journalist = Journalist.objects.create(user=self.user, publisher=self.publisher)

    def test_journalist_can_create_newsletter(self):
        """
        Verify that a logged-in journalist can post valid newsletter data
        to the 'newsletter_create' view and that the newsletter is created properly.
        
        Assertions:
        - The HTTP response redirects (status code 302).
        - A Newsletter instance is created in the database.
        - The newsletter's title matches the posted data.
        - The newsletter is associated with the correct publisher.
        """
        # Log in the test client as the journalist user
        self.client.login(username="journalist", password="testpass")

        # Submit POST request to create newsletter
        response = self.client.post(reverse('newsletter_create'), {
            'title': 'Test Newsletter',
            'content': 'This is a test newsletter.',
        })

        # Check for redirect after successful creation
        self.assertEqual(response.status_code, 302)  # Usually redirects to dashboard or list page

        # Retrieve the created newsletter from the database
        newsletter = Newsletter.objects.first()

        # Verify newsletter creation and correctness of fields
        self.assertIsNotNone(newsletter)
        self.assertEqual(newsletter.title, 'Test Newsletter')
        self.assertEqual(newsletter.publisher, self.publisher)
