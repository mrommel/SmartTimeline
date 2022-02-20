import locale
from collections import defaultdict
from datetime import date, timezone, datetime

from google_play_scraper import app as GoogleApp

from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import loader
from django.utils import translation

from cms.models import Content
from .form import AddRatingsForm, AddVersionModelForm, AddActiveUsersForm
from .models import App, Version, Rating, SemanticVersion, ActiveUsers
from .utils import first, ChartData, ChartDataset, ChartMarker, prev_two_month, MonthYear, scrape_ios_rating


def index(request):
    """
    main page

    :param request: request
    :return: response
    """
    app_list = App.objects.all

    try:
        content_data = Content.objects.get(pk=1)
    except Content.DoesNotExist:
        content_data = None

    template = loader.get_template('timeline/dashboard.html')
    context = {
        'app_list': app_list,
        'title': 'Dashboard',
        'content': content_data
    }
    return HttpResponse(template.render(context, request))


def apps(request):
    """
    apps page

    :param request: request
    :return: response
    """
    app_list = App.objects.all
    template = loader.get_template('timeline/apps.html')
    context = {
        'app_list': app_list,
        'title': 'Apps'
    }
    return HttpResponse(template.render(context, request))


def app(request, app_id):
    """
    app page

    :param app_id: id of app
    :param request: request
    :return: response
    """
    try:
        app_val = App.objects.get(pk=app_id)
    except Version.DoesNotExist:
        app_val = None

    chart_data = ChartData()

    # get all dates
    for rating in Rating.objects.order_by('pub_date'):
        chart_data.timeline.append(rating.pub_date)

    # remove duplicates
    chart_data.timeline = list(set(chart_data.timeline))

    # sort
    chart_data.timeline.sort()

    # prefill
    chart_dataset = ChartDataset(app_val.name, app_val.color, app_val.solid)
    for _ in chart_data.timeline:
        chart_dataset.data.append('0.00')

    chart_data.datasets.append(chart_dataset)

    # actually fill
    for rating in Rating.objects.filter(app=app_val).order_by('pub_date'):
        index_val = chart_data.timeline.index(rating.pub_date)

        dataset = next((x for x in chart_data.datasets if x.name == rating.app.name), None)
        if dataset is not None:
            dataset.data[index_val] = rating.rating

    for version in Version.objects.filter(app=app_val):
        timeline_item = first(chart_data.timeline, condition=lambda x: x >= version.pub_date)
        timeline_index = chart_data.timeline.index(timeline_item)

        marker_text = '%s#%s' % (version.app.name_without_os(), version.name)
        chart_data.markers.append(ChartMarker(version.app.name, timeline_index, marker_text))

    template = loader.get_template('timeline/app.html')
    context = {
        'app': app_val,
        'title': 'App - %s' % app_val.name,
        'chart_data': chart_data
    }
    return HttpResponse(template.render(context, request))


def releases_redirect(request):
    """
    releases page

    :param request: request
    :return: response
    """
    response = redirect('/timeline/releases/all')
    return response


def releases_all(request):
    """
    all releases page

    :param request: request
    :return: response
    """
    today = date.today()
    release_month = today.month
    release_year = today.year

    app_list = App.objects.all
    release_list = Version.objects.order_by('-pub_date')

    major_releases_month = 0
    minor_releases_month = 0
    patch_releases_month = 0
    releases_year = 0

    last_month = -1

    month_list = []

    for release_item in release_list:

        if release_item.pub_date.year == release_year:
            releases_year = releases_year + 1

        if release_item.pub_date.month == release_month and release_item.pub_date.year == release_year:
            if release_item.semantic_version == SemanticVersion.MAJOR.value:
                major_releases_month = major_releases_month + 1
            if release_item.semantic_version == SemanticVersion.MINOR.value:
                minor_releases_month = minor_releases_month + 1
            if release_item.semantic_version == SemanticVersion.PATCH.value:
                patch_releases_month = patch_releases_month + 1

        if release_item.pub_date.month != last_month:
            release_item.first = True
        else:
            release_item.first = False

        last_month = release_item.pub_date.month

    for release_item in Version.objects.all().order_by('-pub_date'):

        month_item = MonthYear(release_item.pub_date.month, release_item.pub_date.year)
        if month_item not in month_list:
            month_list.append(month_item)

    temp = defaultdict(list)
    for item in month_list:
        temp[item.year].append(item.month)

    month_dict = dict((key, tuple(val)) for key, val in temp.items())

    my_date = datetime(release_year, release_month, 1, 4, tzinfo=timezone.utc)
    locale.setlocale(locale.LC_TIME, translation.to_locale(translation.get_language()))
    release_month_str = my_date.strftime("%B")

    template = loader.get_template('timeline/releases.html')
    context = {
        'app_list': app_list,
        'title': 'Releases',
        'release_list': release_list,
        'major_releases_month': major_releases_month,
        'minor_releases_month': minor_releases_month,
        'patch_releases_month': patch_releases_month,
        'release_month': release_month_str,
        'releases_year': releases_year,
        'month_list': month_list,
        'month_dict': month_dict
    }
    return HttpResponse(template.render(context, request))


def releases(request, release_month, release_year):
    """
    releases page

    :param release_month:
    :param release_year:
    :param request: request
    :return: response
    """
    app_list = App.objects.all
    release_list = Version.objects.filter(Q(pub_date__month=release_month), Q(pub_date__year=release_year)).order_by(
        '-pub_date')
    release_list_all = Version.objects.order_by('-pub_date')

    major_releases_month = 0
    minor_releases_month = 0
    patch_releases_month = 0
    releases_year = 0

    last_month = -1

    month_list = []

    for release_item in release_list_all:

        if release_item.pub_date.year == release_year:
            releases_year = releases_year + 1

    for release_item in release_list:

        if release_item.pub_date.month == release_month and release_item.pub_date.year == release_year:
            if release_item.semantic_version == SemanticVersion.MAJOR.value:
                major_releases_month = major_releases_month + 1
            if release_item.semantic_version == SemanticVersion.MINOR.value:
                minor_releases_month = minor_releases_month + 1
            if release_item.semantic_version == SemanticVersion.PATCH.value:
                patch_releases_month = patch_releases_month + 1

        if release_item.pub_date.month != last_month:
            release_item.first = True
        else:
            release_item.first = False

        last_month = release_item.pub_date.month

    for release_item in Version.objects.all().order_by('-pub_date'):

        month_item = MonthYear(release_item.pub_date.month, release_item.pub_date.year)
        if month_item not in month_list:
            month_list.append(month_item)

    temp = defaultdict(list)
    for item in month_list:
        temp[item.year].append(item.month)

    month_dict = dict((key, tuple(val)) for key, val in temp.items())

    my_date = datetime(release_year, release_month, 1, 4, tzinfo=timezone.utc)
    locale.setlocale(locale.LC_TIME, translation.to_locale(translation.get_language()))
    release_month_str = my_date.strftime("%B")

    template = loader.get_template('timeline/releases.html')
    context = {
        'app_list': app_list,
        'title': 'Releases',
        'release_list': release_list,
        'major_releases_month': major_releases_month,
        'minor_releases_month': minor_releases_month,
        'patch_releases_month': patch_releases_month,
        'release_month': release_month_str,
        'releases_year': releases_year,
        'month_list': month_list,
        'month_dict': month_dict
    }
    return HttpResponse(template.render(context, request))


def add_release(request, release_id=-1):
    """
    add new release

    :param release_id:
    :param request:
    :return:
    """
    date_val = date.today()

    try:
        version = Version.objects.get(pk=release_id)
    except Version.DoesNotExist:
        version = None

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddVersionModelForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/timeline/releases?action=added')

    # if a GET (or any other method) we'll create a blank form
    else:
        if version is not None:
            initial = {
                'app': version.app,
                'name': version.name,
                'pub_date': version.pub_date,
                'changelog': version.changelog}
            form = AddVersionModelForm(initial=initial)
        else:
            form_data = {'pub_date': date_val}
            form = AddVersionModelForm(form_data)

    return render(request, 'timeline/release_form.html', {'form': form})

def ratings_current(request):

    today = date.today()
    rating_month = today.month
    rating_year = today.year

    return ratings(request, rating_month, rating_year)

def ratings(request, rating_month, rating_year):
    """
    ratings page

    :param request: request
    :return: response
    """
    app_list = App.objects.all
    template = loader.get_template('timeline/ratings.html')

    chart_data = ChartData()

    # get all dates
    for rating in Rating.objects.order_by('pub_date'):
        if rating.pub_date.year < rating_year or (rating.pub_date.year == rating_year and rating.pub_date.month <= rating_month):
            print("%d-%d <= %d-%d" % (rating.pub_date.year, rating.pub_date.month, rating_year, rating_month))
            chart_data.timeline.append(rating.pub_date)
        else:
            print("%d-%d > %d-%d" % (rating.pub_date.year, rating.pub_date.month, rating_year, rating_month))

    # remove duplicates
    chart_data.timeline = list(set(chart_data.timeline))

    # sort
    chart_data.timeline.sort()

    # prefill
    for app_val in App.objects.all():
        chart_dataset = ChartDataset(app_val.name, app_val.color, app_val.solid)
        for _ in chart_data.timeline:
            chart_dataset.data.append('0.00')
            chart_dataset.delta.append('0.00')

        chart_data.datasets.append(chart_dataset)

    # actually fill
    for rating in Rating.objects.order_by('pub_date'):
        try:
            index_val = chart_data.timeline.index(rating.pub_date)

            dataset = next((x for x in chart_data.datasets if x.name == rating.app.name), None)
            if dataset is not None:
                dataset.data[index_val] = rating.rating
        except ValueError:
            continue

    # problem: there must be a rating after the last release
    for version in Version.objects.all():
        try:
            timeline_item = first(chart_data.timeline, condition=lambda x: x >= version.pub_date)
            timeline_index = chart_data.timeline.index(timeline_item)

            marker_text = '%s#%s' % (version.app.name_without_os(), version.name)
            chart_data.markers.append(ChartMarker(version.app.name, timeline_index, marker_text))
        except StopIteration:
            print("cant add %s" % version)

    context = {
        'app_list': app_list,
        'title': 'Ratings',
        'type': 'normal',
        'chart_data': chart_data
    }
    return HttpResponse(template.render(context, request))


def ratings_last_months(request):
    """
    ratings page of last two month

    :param request: request
    :return: response
    """
    app_list = App.objects.all
    template = loader.get_template('timeline/ratings.html')

    chart_data = ChartData()

    # get all dates
    two_month_ago = prev_two_month()
    for rating in Rating.objects.order_by('pub_date'):
        if rating.pub_date > two_month_ago.date():
            chart_data.timeline.append(rating.pub_date)

    # remove duplicates
    chart_data.timeline = list(set(chart_data.timeline))

    # sort
    chart_data.timeline.sort()

    # prefill
    for app_val in App.objects.all():
        chart_dataset = ChartDataset(app_val.name, app_val.color, app_val.solid)
        for _ in chart_data.timeline:
            chart_dataset.data.append('0.00')

        chart_data.datasets.append(chart_dataset)

    # actually fill
    for rating in Rating.objects.order_by('pub_date'):
        try:
            index_val = chart_data.timeline.index(rating.pub_date)

            dataset = next((x for x in chart_data.datasets if x.name == rating.app.name), None)
            if dataset is not None:
                dataset.data[index_val] = rating.rating
        except ValueError:
            pass

    # problem: there must be a rating after the last release
    for version in Version.objects.all():
        try:
            timeline_item = first(chart_data.timeline, condition=lambda x: x >= version.pub_date)
            timeline_index = chart_data.timeline.index(timeline_item)

            marker_text = '%s#%s' % (version.app.name_without_os(), version.name)
            chart_data.markers.append(ChartMarker(version.app.name, timeline_index, marker_text))
        except StopIteration as e:
            print("cant add %s -> %s" % (version, e))

    context = {
        'app_list': app_list,
        'title': 'Ratings',
        'type': 'last',
        'chart_data': chart_data
    }
    return HttpResponse(template.render(context, request))


def add_ratings(request):
    """
    add new rating

    :param request:
    :return:
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddRatingsForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # get data
            pub_date = form.cleaned_data['date']
            rating_myf_android = form.cleaned_data['myf_android']
            rating_myf_ios = form.cleaned_data['myf_ios']
            rating_fon_android = form.cleaned_data['fon_android']
            rating_fon_ios = form.cleaned_data['fon_ios']
            rating_wlan_android = form.cleaned_data['wlan_android']
            rating_wlan_ios = form.cleaned_data['wlan_ios']
            rating_tv_android = form.cleaned_data['tv_android']
            rating_tv_ios = form.cleaned_data['tv_ios']
            rating_smart_home_android = form.cleaned_data['smart_home_android']
            rating_smart_home_ios = form.cleaned_data['smart_home_ios']

            # myfritz
            app_myf_android = App.objects.get(id=1)
            myf_android = Rating(app=app_myf_android, pub_date=pub_date, rating=rating_myf_android)
            myf_android.save()

            app_myf_ios = App.objects.get(id=2)
            myf_ios = Rating(app=app_myf_ios, pub_date=pub_date, rating=rating_myf_ios)
            myf_ios.save()

            # fon
            app_fon_android = App.objects.get(id=3)
            myf_android = Rating(app=app_fon_android, pub_date=pub_date, rating=rating_fon_android)
            myf_android.save()

            app_fon_ios = App.objects.get(id=4)
            myf_ios = Rating(app=app_fon_ios, pub_date=pub_date, rating=rating_fon_ios)
            myf_ios.save()

            # wlan
            app_wlan_android = App.objects.get(id=5)
            wlan_android = Rating(app=app_wlan_android, pub_date=pub_date, rating=rating_wlan_android)
            wlan_android.save()

            app_wlan_ios = App.objects.get(id=6)
            wlan_ios = Rating(app=app_wlan_ios, pub_date=pub_date, rating=rating_wlan_ios)
            wlan_ios.save()

            # tv
            app_tv_android = App.objects.get(id=7)
            tv_android = Rating(app=app_tv_android, pub_date=pub_date, rating=rating_tv_android)
            tv_android.save()

            app_tv_ios = App.objects.get(id=8)
            tv_ios = Rating(app=app_tv_ios, pub_date=pub_date, rating=rating_tv_ios)
            tv_ios.save()

            # smart home
            app_smart_home_android = App.objects.get(id=9)
            smart_home_android = Rating(app=app_smart_home_android, pub_date=pub_date, rating=rating_smart_home_android)
            smart_home_android.save()

            app_smart_home_ios = App.objects.get(id=10)
            smart_home_ios = Rating(app=app_smart_home_ios, pub_date=pub_date, rating=rating_smart_home_ios)
            smart_home_ios.save()

            # redirect to a new URL:
            return HttpResponseRedirect('/timeline/ratings?action=added')

    # if a GET (or any other method) we'll create a blank form
    else:
        date_val = date.today()

        result_myf_android = GoogleApp('de.avm.android.myfritz2', lang='de', country='de')
        if result_myf_android["score"] is not None:
            myf_android = "%.2f" % result_myf_android["score"]
        else:
            myf_android = ""

        result_fon_android = GoogleApp('de.avm.android.fritzapp', lang='de', country='de')
        if result_fon_android["score"] is not None:
            fon_android = "%.2f" % result_fon_android["score"]
        else:
            fon_android = ""

        result_wlan_android = GoogleApp('de.avm.android.wlanapp', lang='de', country='de')
        if result_wlan_android["score"] is not None:
            wlan_android = "%.2f" % result_wlan_android["score"]
        else:
            wlan_android = ""

        result_tv_android = GoogleApp('de.avm.android.fritzapptv', lang='de', country='de')
        if result_tv_android["score"] is not None:
            tv_android = "%.2f" % result_tv_android["score"]
        else:
            tv_android = ""

        result_smart_home_android = GoogleApp('de.avm.android.smarthome', lang='de', country='de')
        if result_smart_home_android["score"] is not None:
            smart_home_android = "%.2f" % result_smart_home_android["score"]
        else:
            smart_home_android = ""

        myf_ios = scrape_ios_rating(620435371)  # MyFRITZ!App iOS
        fon_ios = scrape_ios_rating(372184475)  # FRITZ!App FON iOS
        wlan_ios = scrape_ios_rating(1351324738)  # FRITZ!App WLAN iOS
        tv_ios = scrape_ios_rating(911447974)  # FRITZ!App TV iOS
        smart_home_ios = scrape_ios_rating(1477824478)  # FRITZ!App Smart Home iOS

        form_data = {
            'date': date_val,
            'myf_android': myf_android, 'myf_ios': myf_ios,
            'fon_android': fon_android, 'fon_ios': fon_ios,
            'wlan_android': wlan_android, 'wlan_ios': wlan_ios,
            'tv_android': tv_android, 'tv_ios': tv_ios,
            'smart_home_android': smart_home_android, 'smart_home_ios': smart_home_ios
        }

        form = AddRatingsForm(form_data)

    return render(request, 'timeline/rating_form.html', {'form': form})


def active_users(request):
    """
        active users page

        :param request: request
        :return: response
        """
    app_list = App.objects.all()
    chart_data = ChartData()

    for app in app_list:
        current_users_val = app.current_users().users
        last_month_users_val = app.last_month_users().users
        twelve_month_users_val = app.twelve_month_ago_users().users

        last_month_value = 100.0 - float(int(last_month_users_val / current_users_val * 10000.0)) / 100.0
        app.delta_last_month = "{:.2f}".format(last_month_value)
        if last_month_value > 0:
            app.delta_last_month = '+%s' % app.delta_last_month

        last_year_value = 100.0 - float(int(twelve_month_users_val / current_users_val * 10000.0)) / 100.0
        app.delta_last_year = "{:.2f}".format(last_year_value)
        if last_year_value > 0:
            app.delta_last_year = '+%s' % app.delta_last_year

    # get all dates
    for active_user in ActiveUsers.objects.order_by('date'):
        chart_data.timeline.append(active_user.date)

    # remove duplicates
    chart_data.timeline = list(set(chart_data.timeline))

    # sort
    chart_data.timeline.sort()

    # prefill
    for app_val in App.objects.all():
        chart_dataset = ChartDataset(app_val.name, app_val.color, app_val.solid)
        for _ in chart_data.timeline:
            chart_dataset.data.append('0.00')
            chart_dataset.delta.append('0.00')

        chart_data.datasets.append(chart_dataset)

    # actually fill
    for active_user in ActiveUsers.objects.order_by('date'):
        try:
            index_val = chart_data.timeline.index(active_user.date)
            previous_active_users = None
            if index_val > 0:
                previous_active_users = active_user.app.active_users()[index_val - 1]
            previous_val = active_user.users

            if previous_active_users is not None:
                previous_val = previous_active_users.users

            dataset = next((x for x in chart_data.datasets if x.name == active_user.app.name), None)
            if dataset is not None:
                dataset.data[index_val] = active_user.users
                dataset.delta[index_val] = active_user.users - previous_val  # not valid
        except ValueError:
            pass

    template = loader.get_template('timeline/active_users.html')

    context = {
        'app_list': app_list,
        'title': 'Active Users',
        'chart_data': chart_data
    }
    return HttpResponse(template.render(context, request))


def add_active_users(request):
    """
    add new active users

    :param request:
    :return:
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddActiveUsersForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # get data
            date_val = form.cleaned_data['date']
            users_myf_android = form.cleaned_data['myf_android']
            users_myf_ios = form.cleaned_data['myf_ios']
            users_fon_android = form.cleaned_data['fon_android']
            users_fon_ios = form.cleaned_data['fon_ios']
            users_wlan_android = form.cleaned_data['wlan_android']
            users_wlan_ios = form.cleaned_data['wlan_ios']
            users_tv_android = form.cleaned_data['tv_android']
            users_tv_ios = form.cleaned_data['tv_ios']
            users_smart_home_android = form.cleaned_data['smart_home_android']
            users_smart_home_ios = form.cleaned_data['smart_home_ios']

            # myfritz
            app_myf_android = App.objects.get(id=1)
            myf_android = ActiveUsers(app=app_myf_android, date=date_val, users=users_myf_android)
            myf_android.save()

            app_myf_ios = App.objects.get(id=2)
            myf_ios = ActiveUsers(app=app_myf_ios, date=date_val, users=users_myf_ios)
            myf_ios.save()

            # fon
            app_fon_android = App.objects.get(id=3)
            fon_android = ActiveUsers(app=app_fon_android, date=date_val, users=users_fon_android)
            fon_android.save()

            app_fon_ios = App.objects.get(id=4)
            fon_ios = ActiveUsers(app=app_fon_ios, date=date_val, users=users_fon_ios)
            fon_ios.save()

            # wlan
            app_wlan_android = App.objects.get(id=5)
            wlan_android = ActiveUsers(app=app_wlan_android, date=date_val, users=users_wlan_android)
            wlan_android.save()

            app_wlan_ios = App.objects.get(id=6)
            wlan_ios = ActiveUsers(app=app_wlan_ios, date=date_val, users=users_wlan_ios)
            wlan_ios.save()

            # tv
            app_tv_android = App.objects.get(id=7)
            tv_android = ActiveUsers(app=app_tv_android, date=date_val, users=users_tv_android)
            tv_android.save()

            app_tv_ios = App.objects.get(id=8)
            tv_ios = ActiveUsers(app=app_tv_ios, date=date_val, users=users_tv_ios)
            tv_ios.save()

            # smart home
            app_smart_home_android = App.objects.get(id=9)
            smart_home_android = ActiveUsers(app=app_smart_home_android, date=date_val, users=users_smart_home_android)
            smart_home_android.save()

            app_smart_home_ios = App.objects.get(id=10)
            smart_home_ios = ActiveUsers(app=app_smart_home_ios, date=date_val, users=users_smart_home_ios)
            smart_home_ios.save()

            # redirect to a new URL:
            return HttpResponseRedirect('/timeline/active_users/?action=added')

    # if a GET (or any other method) we'll create a blank form
    else:
        date_val = date.today()
        form_data = {'date_0': date_val.month, 'date_1': date_val.year}

        form = AddActiveUsersForm(form_data)

        for field in form.fields:
            form.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    return render(request, 'timeline/active_users_form.html', {'form': form})
