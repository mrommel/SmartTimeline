from datetime import date

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import loader

from cms.models import Content
from .form import AddRatingsForm, AddVersionModelForm
from .models import App, Version, Rating
from .utils import first, ChartData, ChartDataset, ChartMarker, prev_two_month


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


def releases(request):
    """
    releases page

    :param request: request
    :return: response
    """
    app_list = App.objects.all
    release_list = Version.objects.order_by('-pub_date')

    last_month = 27
    for release_item in release_list:
        if release_item.pub_date.month != last_month:
            release_item.first = True
        else:
            release_item.first = False

        last_month = release_item.pub_date.month

    template = loader.get_template('timeline/releases.html')
    context = {
        'app_list': app_list,
        'title': 'Releases',
        'release_list': release_list
    }
    return HttpResponse(template.render(context, request))


def add_release(request, release_id=-1):
    """
    add new release

    :param release_id:
    :param request:
    :return:
    """

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
            form = AddVersionModelForm()

    return render(request, 'timeline/release_form.html', {'form': form})


def ratings(request):
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
        index_val = chart_data.timeline.index(rating.pub_date)

        dataset = next((x for x in chart_data.datasets if x.name == rating.app.name), None)
        if dataset is not None:
            dataset.data[index_val] = rating.rating

    # problem: there must be a rating after the last release
    for version in Version.objects.all():
        try:
            timeline_item = first(chart_data.timeline, condition=lambda x: x >= version.pub_date)
            timeline_index = chart_data.timeline.index(timeline_item)

            marker_text = '%s#%s' % (version.app.name_without_os(), version.name)
            chart_data.markers.append(ChartMarker(version.app.name, timeline_index, marker_text))
        except StopIteration as e:
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

        from google_play_scraper import app
        result_myf_android = app('de.avm.android.myfritz2', lang='en', country='us')
        myf_android = "%.2f" % result_myf_android["score"]

        result_fon_android = app('de.avm.android.fritzapp', lang='en', country='us')
        fon_android = "%.2f" % result_fon_android["score"]

        result_wlan_android = app('de.avm.android.wlanapp', lang='en', country='us')
        wlan_android = "%.2f" % result_wlan_android["score"]

        result_tv_android = app('de.avm.android.fritzapptv', lang='en', country='us')
        tv_android = "%.2f" % result_tv_android["score"]

        result_smart_home_android = app('de.avm.android.smarthome', lang='en', country='us')
        smart_home_android = "%.2f" % result_smart_home_android["score"]

        form_data = {'date': date_val, 'myf_android': myf_android, 'fon_android': fon_android, 'wlan_android': wlan_android,
                     'tv_android': tv_android, 'smart_home_android': smart_home_android}

        form = AddRatingsForm(form_data)

    return render(request, 'timeline/rating_form.html', {'form': form})
