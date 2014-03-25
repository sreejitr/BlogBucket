from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

#To manually create HttpResponses or raise an Http404 exception
from django.http import HttpResponse, Http404

#Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

#Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

# Helper function to guess a MIME type from a file name
from mimetypes import guess_type

from django.contrib.auth.tokens import default_token_generator

# To send emails from Django
from django.core.mail import send_mail

import pdb

from models import *
from forms import *


def home(request):
    users = User.objects.all()
    follows = []
    posts = []
    logged_in = None
    try:
        if request.user.is_authenticated():
            curr_user = User.objects.get(id=request.user.id)
            logged_in = True
            try:
                follower_user = Followers.objects.get(user=curr_user)
            except Followers.DoesNotExist:
                follower_user = None
            if follower_user:
                follows = follower_user.follows.all()
                for u in follows:
                    posts.extend(Blogs.get_blogs(u))
                posts = sorted(posts, key=lambda x: x.created_date, reverse=True)
    except User.DoesNotExist:
        logged_in = False

    context = {'users' : users, 'follows' : follows, 'posts' : posts, 'logged_in': logged_in}
    return render(request, 'blog/home.html', context)


def index(request, id):
    id_belongs_to_logged_in_user = False
    users = User.objects.all()
    user = User.objects.get(id=id)
    posts = Blogs.get_blogs(user)
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = None
    if request.user.is_authenticated():
        if request.user.id == id:
            id_belongs_to_logged_in_user = True
        logged_in = True
        context = {'form':BlogsForm(), 'posts' : posts, 'profile' : profile, 'logged_in' : logged_in, 'id_belongs_to_logged_in_user' : id_belongs_to_logged_in_user}
    else:
        logged_in = False
        context = {'users' : users, 'posts' : posts, 'profile' : profile, 'logged_in' : logged_in, 'id_belongs_to_logged_in_user' : id_belongs_to_logged_in_user}
    return render(request, 'blog/index.html', context)


@login_required
@transaction.commit_on_success
def follow(request, id):
    logged_in = True
    posts = []
    users = User.objects.all()
    get_user = None
    user_to_follow = User.objects.get(id=id)
    get_user = User.objects.get(id=request.user.id)
    if not user_to_follow == get_user:
        try:
            u = Followers.objects.get(user=get_user)
        except Followers.DoesNotExist:
            u = Followers(user=get_user)
            u.save()
        followers = u.follows.all()

        if user_to_follow not in followers:
            u.follows.add(user_to_follow)
        else:
            u.follows.remove(user_to_follow)
            u.save
        
    return home(request)


@login_required
@transaction.commit_on_success
def manage_posts(request):
    user = User.objects.get(id=request.user.id)
    users = User.objects.all()
    form = BlogsForm()
    profile = None
    posts = []
    if request.method == 'GET':
        posts = Blogs.get_blogs(user)
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            profile = None
    if request.user.is_authenticated():
        logged_in = True
    else:
        logged_in = False
    context = {'users' : users, 'form': form, 'posts' : posts, 'logged_in' : logged_in,  'profile' : profile}
    return render(request, 'blog/manage.html', context)


@login_required
@transaction.commit_on_success
def editprofile(request, id):
    logged_in = True
    users = User.objects.all()
    u = User.objects.get(id=request.user.id)
    posts = Blogs.get_blogs(u)
    profile_to_edit = get_object_or_404(UserProfile, user=request.user, id=id)
    if request.method == 'GET':
        form = UserProfileForm(instance=profile_to_edit)
        context = {'form':form, 'id':id, 'profile': profile_to_edit, 'logged_in' : logged_in, 'users' : users}
        return render(request, 'blog/edit-profile.html', context)

    # if method is POST, get form data to update the model
    form = UserProfileForm(request.POST, instance=profile_to_edit)

    if not form.is_valid():
        context = {'users' : users, 'form':form, 'profile': profile_to_edit, 'logged_in' : logged_in}
        return render(request, 'blog/manage.html', context)

    form.save()
    if request.user.is_authenticated():
        logged_in = True
    else:
        logged_in = False
    context = {'users' : users, 'form':BlogsForm(), 'posts':posts, 'logged_in' : logged_in, 'profile': profile_to_edit}
    return render(request, 'blog/manage.html', context)

@login_required
def create_post(request):
    logged_in = True
    users = User.objects.all()
    user = User.objects.get(id=request.user.id)
    new_post = Blogs(user=user)
    form = BlogsForm(request.POST, request.FILES, instance=new_post)
    if not form.is_valid():
        posts = Blogs.get_blogs(request.user)
        try:
            profile = UserProfile.objects.get(id=request.user.id)
        except UserProfile.DoesNotExist:
            profile = None
        context = {'users' : users, 'form':form, 'posts': posts, 'profile': profile, 'logged_in' : logged_in}
        return render(request, 'blog/manage.html', context)
    try:
        profile = UserProfile.objects.get(id=request.user.id)
    except UserProfile.DoesNotExist:
        profile = None
    form.save()
    posts = Blogs.get_blogs(user)
    context = {'users' : users, 'form':BlogsForm(), 'posts': posts, 'profile': profile, 'logged_in' : logged_in}
    return render(request, 'blog/manage.html', context)


@login_required
@transaction.commit_on_success
def delete_post(request, id):
    logged_in = True
    errors = []
    users = User.objects.all()
    # Deletes post if the logged-in user has a post matching the id
    try:
        post_to_delete = Blogs.objects.get(id=id, user=request.user)
        post_to_delete.delete()
    except ObjectDoesNotExist:
        errors.append('The post does not exist in your blog.')
    
    posts = Blogs.get_blogs(request.user)
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None
    context = {'users' : users, 'form': BlogsForm, 'posts' : posts, 'errors' : errors, 'profile': profile, 'logged_in' : logged_in}
    return render(request, 'blog/manage.html', context)


@transaction.commit_on_success
def register(request):
    users = User.objects.all()
    context = {}
    token = ''
    
    # Display the registration form if this is a GET request
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'blog/register.html', context)
    
    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form
    
    # Validates the form.
    if not form.is_valid():
        return render(request, 'blog/register.html', context)
    
    # If we get here the form data was valid.  Register and login the user.
    new_user = User.objects.create_user(first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'],
                                        username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'])
    new_user.is_active=False
    new_user.save()
    
    token = default_token_generator.make_token(new_user)
    email_body = """Welcome to BlogBucket. Please click on the link below to verify your email address and complete the registration process:
            http://%s/blog/confirm?username=%s&token=%s""" % (request.get_host(), new_user.username, token)
                
    send_mail(subject="Verify your email address",
              message= email_body,
              from_email="sreejitr@andrew.cmu.edu",
              recipient_list=[new_user.email])
        
    context['email'] = form.cleaned_data['email']
    context['users'] = users
    return render(request, 'blog/needs-confirmation.html', context)
    
    # Logs in the new user and redirects to his/her blog
    #new_user = authenticate(username=form.cleaned_data['username'], \
    password=form.cleaned_data['password1']
    #login(request, new_user)
    #return redirect(reverse('home'))
    

@transaction.commit_on_success
def confirm_registration(request):
    context = {}
    username = request.GET.get('username')
    token = request.GET.get('token')
    new_user = User.objects.get(username=username)
    if(default_token_generator.check_token(new_user, token)):
        # Logs in the new user and redirects to his/her blog
        if (new_user.is_active != True):
            new_user.is_active = True
            new_user.save()
            #Creates profile
            fullname = new_user.first_name + " " + new_user.last_name
            user_profile = UserProfile(user=new_user, name=fullname, token=token)
            user_profile.save()
            #login(new_user)
        else:
            context = {'active_user': True}
        return render(request, 'blog/confirm-registration.html', context)

def get_users(request):
    context = {'users': User.objects.all()}
    return render(request, 'blog/users.xml', context, content_type='application/xml')


def aboutus(request):
    users = User.objects.all()
    if request.user.is_authenticated():
        logged_in = True
    else:
        logged_in = False
    return render(request, 'blog/aboutus.html', {'users' : users, 'logged_in' : logged_in})

def contactus(request):
    users = User.objects.all()
    if request.user.is_authenticated():
        logged_in = True
    else:
        logged_in = False
    return render(request, 'blog/contactus.html', {'users' : users, 'logged_in' : logged_in})





