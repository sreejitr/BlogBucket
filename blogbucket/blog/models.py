from django.db import models
from datetime import datetime

# Models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Blogs(models.Model):
    text = models.CharField(max_length=160)
    created_date = models.DateTimeField(default=datetime.now, blank=True, editable=False)
    #modified_date = models.DateTimeField(default=datetime.now, blank=True, editable=False)
    picture = models.ImageField(upload_to="media", blank=True)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return self.text

    @staticmethod
    def get_blogs(user):
        return Blogs.objects.filter(user=user).order_by('-created_date')


class UserProfile(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=500, default="", blank=True)
    phone = models.CharField(max_length=500, default="", blank=True)
    interests = models.CharField(max_length=200, default="", blank=True)
    token = models.CharField(max_length=1000)
    
    def __unicode__(self):
        return self.name


class Followers(models.Model):
    user = models.ForeignKey(User, unique = True, related_name='user')
    follows = models.ManyToManyField(User, related_name="follows", symmetrical=False, blank=True)

#def __unicode__(self):
#return unicode(self.user)

