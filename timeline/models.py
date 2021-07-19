from datetime import date

from colorfield.fields import ColorField
from django.db import models
from django.utils.translation import gettext_lazy as _
from month.models import MonthField
from timeline.utils import month_delta


class MobileOS(models.TextChoices):
    ANDROID = 'And', _('Android')
    IOS = 'iOS', _('iOS')


class SemanticVersion(models.TextChoices):
    MAJOR = 'Maj', _('Major')
    MINOR = 'Min', _('Minor')
    PATCH = 'Pat', _('Patch')


class App(models.Model):
    name = models.CharField(max_length=200)
    mobile_os = models.CharField(max_length=3, choices=MobileOS.choices, default=MobileOS.ANDROID, )
    color = ColorField(default='#000000')
    solid = models.BooleanField(default=True)

    def name_without_os(self):

        return self.name.replace("Android", "").replace("iOS", "")

    def current_version(self):

        return Version.objects.filter(app=self).latest('pub_date')

    def versions(self):
        return Version.objects.filter(app=self).order_by('-pub_date')

    def current_rating(self):

        return Rating.objects.filter(app=self).latest('pub_date')

    def last_month_rating(self):

        all_ratings = Rating.objects.filter(app=self).order_by('pub_date')
        last_month = month_delta(date.today(), -1)
        return next((x for x in all_ratings if x.pub_date > last_month), None)

    def last_month_rating_delta(self):

        curr = self.current_rating()
        last = self.last_month_rating()

        if curr is not None and last is not None:
            return curr.rating - last.rating

        return 0.0

    def six_month_ago_rating(self):

        all_ratings = Rating.objects.filter(app=self).order_by('pub_date')
        last_month = month_delta(date.today(), -6)
        return next((x for x in all_ratings if x.pub_date > last_month), None)

    def six_month_ago_rating_delta(self):

        curr = self.current_rating()
        last = self.six_month_ago_rating()

        if curr is not None and last is not None:
            return curr.rating - last.rating

        return 0.0

    def twelve_month_ago_rating(self):

        all_ratings = Rating.objects.filter(app=self).order_by('pub_date')
        last_month = month_delta(date.today(), -12)
        return next((x for x in all_ratings if x.pub_date > last_month), None)

    def twelve_month_ago_rating_delta(self):

        curr = self.current_rating()
        last = self.twelve_month_ago_rating()

        if curr is not None and last is not None:
            return curr.rating - last.rating

        return 0.0

    # ...
    def __str__(self):
        return self.name


class Version(models.Model):
    name = models.CharField(max_length=200)
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    semantic_version = models.CharField(max_length=3, choices=SemanticVersion.choices, default=SemanticVersion.PATCH, )
    changelog = models.CharField(max_length=1024)
    pub_date = models.DateField('date published')

    # ...
    def __str__(self):
        return '%s, Version %s (%s)' % (self.app.name, self.name, self.semantic_version)


class Rating(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    pub_date = models.DateField('date published')

    def rating_percent(self):
        return str(int(self.rating * 20))

    # ...
    def __str__(self):
        return _('Rating of %s at %s') % (self.app.name, self.pub_date)


class ActiveUsers(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    users = models.IntegerField()
    date = MonthField('date')

    def __str__(self):
        return _('Number of Users of %s at %s') % (self.app.name, self.date)
