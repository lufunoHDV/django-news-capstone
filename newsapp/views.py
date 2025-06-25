from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden
from django.contrib import messages

from .models import Article, Newsletter, CustomUser, Publisher
from .forms import (
    CustomUserCreationForm,
    ArticleForm,
    NewsletterForm,
    SubscriptionForm,
)


# Role check helper functions for access control
def is_journalist(user):
    return user.groups.filter(name='Journalist').exists()


def is_editor(user):
    return user.groups.filter(name='Editor').exists()


def is_reader(user):
    return user.groups.filter(name='Reader').exists()


# Home page view - accessible to all users
def home_view(request):
    return render(request, 'newsapp/home.html')


# User registration view
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            try:
                group = Group.objects.get(name=role)
                user.groups.add(group)
            except Group.DoesNotExist:
                messages.warning(request, f"The group '{role}' does not exist.")
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! You are now registered as a {role}.")
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# User login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


# User logout view
def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('home')


# Dashboard view showing articles from subscribed publishers and journalists (for readers)
@login_required
def dashboard_view(request):
    followed_articles = []
    if is_reader(request.user):
        pub_articles = Article.objects.filter(
            approved=True, publisher__in=request.user.subscribed_publishers.all()
        )
        jour_articles = Article.objects.filter(
            approved=True, author__in=request.user.subscribed_journalists.all()
        )
        followed_articles = pub_articles.union(jour_articles)
    return render(request, 'newsapp/dashboard.html', {
        'followed_articles': followed_articles
    })


# Manage subscriptions - readers can subscribe/unsubscribe to publishers and journalists
@user_passes_test(is_reader)
def manage_subscriptions(request):
    user = request.user
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Subscriptions updated successfully.")
            return redirect('dashboard')
    else:
        form = SubscriptionForm(instance=user)

    return render(request, 'newsapp/subscriptions.html', {'form': form})


# Article list view (role-based)
def article_list_view(request):
    if is_reader(request.user):
        articles = Article.objects.filter(approved=True)
    elif is_editor(request.user):
        articles = Article.objects.all()
    elif is_journalist(request.user):
        articles = Article.objects.filter(author=request.user)
    else:
        return HttpResponseForbidden()
    return render(request, 'newsapp/article_list.html', {'articles': articles})


# Article detail view with permission checks
def article_detail_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.approved or is_editor(request.user) or article.author == request.user:
        return render(request, 'newsapp/article_detail.html', {'article': article})
    messages.error(request, "You do not have permission to access this page.")
    return redirect('dashboard')


# Article creation - journalists only
@user_passes_test(is_journalist)
def article_create_view(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('article_list')
    else:
        form = ArticleForm()
    return render(request, 'newsapp/article_create.html', {'form': form})


# Article update - author or editor only
def article_update_view(request, pk):
    """
    Allow:
    - Authors (journalists) to update their own articles.
    - Editors to update any article.
    """
    article = get_object_or_404(Article, pk=pk)
    
    # Check if user is the author or is an editor
    if request.user == article.author or is_editor(request.user):
        if request.method == 'POST':
            form = ArticleForm(request.POST, instance=article)
            if form.is_valid():
                form.save()
                messages.success(request, "Article updated successfully.")
                return redirect('article_list')
        else:
            form = ArticleForm(instance=article)
        return render(request, 'newsapp/article_update.html', {'form': form})
    
    return HttpResponseForbidden("You do not have permission to edit this article.")


# Article deletion - author or editor only
def article_delete_view(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if request.user == article.author or is_editor(request.user):
        if request.method == 'POST':
            article.delete()
            messages.success(request, "Article deleted successfully.")
            return redirect('article_list')
        return render(request, 'newsapp/article_delete.html', {'article': article})
    else:
        messages.error(request, "You do not have permission to delete this article.")
        return redirect('article_list')


# Article approval - editors only
@user_passes_test(is_editor)
def article_approve_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.approved = True
    article.save()
    messages.success(request, f"Article '{article.title}' approved.")
    return redirect('article_list')


# Newsletter creation - journalists only
@user_passes_test(is_journalist)
def newsletter_create_view(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()
            return redirect('newsletter_list')
    else:
        form = NewsletterForm()
    return render(request, 'newsapp/newsletter_create.html', {'form': form})


# Newsletter list view - role based
def newsletter_list_view(request):
    if is_reader(request.user):
        newsletters = Newsletter.objects.filter()  # adjust filtering if you have a published flag
    elif is_editor(request.user):
        newsletters = Newsletter.objects.all()
    elif is_journalist(request.user):
        newsletters = Newsletter.objects.filter(author=request.user)
    else:
        return HttpResponseForbidden()
    return render(request, 'newsapp/newsletter_list.html', {'newsletters': newsletters})


# Newsletter update - editor or author
@login_required
def newsletter_update_view(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if is_editor(request.user) or request.user == newsletter.author:
        if request.method == 'POST':
            form = NewsletterForm(request.POST, instance=newsletter)
            if form.is_valid():
                form.save()
                return redirect('newsletter_list')
        else:
            form = NewsletterForm(instance=newsletter)
        return render(request, 'newsapp/newsletter_create.html', {'form': form})
    return HttpResponseForbidden()


# Newsletter deletion - editor or author
@login_required
def newsletter_delete_view(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if is_editor(request.user) or request.user == newsletter.author:
        newsletter.delete()
        return redirect('newsletter_list')
    return HttpResponseForbidden()


@login_required
def some_view(request):
    # Just a sample view for demonstration
    return render(request, 'newsapp/some_template.html', {'message': 'This is some view.'})
