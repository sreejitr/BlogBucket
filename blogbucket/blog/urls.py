from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'blog.views.home', name='home'),
    url(r'^confirm$', 'blog.views.confirm_registration', name='confirm'),
    #url(r'^blogbucket$', 'blog.views.info', name='info'),
    url(r'^aboutus$', 'blog.views.aboutus', name='aboutus'),
    url(r'^contactus$', 'blog.views.contactus', name='contactus'),
    url(r'^manage-posts', 'blog.views.manage_posts', name='manage'),
    url(r'^create-post', 'blog.views.create_post', name='create'),
    url(r'^index/(?P<id>\d+)$', 'blog.views.index', name='index'),
    url(r'^follow/(?P<id>\d+)$', 'blog.views.follow', name='follow'),
    url(r'^edit-profile/(?P<id>\d+)$', 'blog.views.editprofile', name='editprofile'),
    url(r'^delete-post/(?P<id>\d+)$', 'blog.views.delete_post', name='delete'),
    # Route for built-in authentication with our own custom login page
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'blog/login.html'}, name='login'),
    # Route to logout a user and send them back to the login page
    url(r'^logout$', 'django.contrib.auth.views.logout_then_login', {'login_url':'/blog/'}, name='logout'),
    url(r'^register$', 'blog.views.register', name='register'),
    url(r'^get-users', 'blog.views.get_users'),
)
