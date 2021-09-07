import pathlib
from operator import attrgetter

from appstoreconnect import Api
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader


def index(request):
    """
    main page

    :param request: request
    :return: response
    """
    file_path = pathlib.Path(__file__).parent.resolve()
    key_file_path = '%s/assets/AuthKey_LDQUAU83WW.p8' % file_path

    api = Api('LDQUAU83WW', key_file_path, '69a6de72-64fe-47e3-e053-5b8c7c11a4d1')

    ios_apps = api.list_apps()
    ios_apps = [app for app in ios_apps if app.name != 'FRITZ!App Fon Lab']
    ios_apps = sorted(ios_apps, key=attrgetter('name'))

    template = loader.get_template('stores/dashboard.html')
    context = {
        'ios_apps': ios_apps,
        'title': 'Dashboard'
    }
    return HttpResponse(template.render(context, request))


# class BetaGroup:
#     """
#     class that holds the chart data ready to be displayed
#     """
#
#     def __init__(self, name, identifier, testers):
#         self.name = name
#         self.identifier = identifier
#         self.testers = testers


def ios_app(request, sku):
    """
    ios app page

    :param request: request
    :param sku: sku
    :return: response
    """
    file_path = pathlib.Path(__file__).parent.resolve()
    key_file_path = '%s/assets/AuthKey_LDQUAU83WW.p8' % file_path

    api = Api('LDQUAU83WW', key_file_path, '69a6de72-64fe-47e3-e053-5b8c7c11a4d1')

    # read app information
    app = api.read_app_information(sku)

    # beta_groups = []
    # for group in app.betaGroups():
    #     #beta_testers = api.list_beta_testers(filters={'betaGroups': '%s' % group.id})
    #     #beta_testers = api.list_beta_testers()
    #     beta_testers = api.list_beta_testers(filters={'apps': sku}, limit=3)
    #     beta_groups.append(BetaGroup(group.name, group.id, beta_testers))

    template = loader.get_template('stores/ios_app.html')
    context = {
        'app': app,
        'title': 'iOS App',
        'beta_groups': app.betaGroups()
    }
    return HttpResponse(template.render(context, request))


def ios_beta_testers(request, id):
    """
    ios app page

    :param request: request
    :param id: group id
    :return: response
    """
    file_path = pathlib.Path(__file__).parent.resolve()
    key_file_path = '%s/assets/AuthKey_LDQUAU83WW.p8' % file_path

    api = Api('LDQUAU83WW', key_file_path, '69a6de72-64fe-47e3-e053-5b8c7c11a4d1')

    # read app information
    beta_group = api.read_beta_group_information(id)
    beta_testers = api.list_beta_testers(filters={'betaGroups': '%s' % id})

    template = loader.get_template('stores/ios_beta_testers.html')
    context = {
        'title': 'iOS App',
        'beta_group': beta_group,
        'beta_testers': beta_testers
    }
    return HttpResponse(template.render(context, request))


class BetaGroup:
    """
    class that holds a beta group
    """

    def __init__(self, beta_group, beta_testers):
        self.beta_group = beta_group
        self.beta_testers = beta_testers


def ios_all_inhouse_beta_testers(request):
    """
    ios all inhouse beta testers page

    :param request: request
    :return: response
    """
    file_path = pathlib.Path(__file__).parent.resolve()
    key_file_path = '%s/assets/AuthKey_LDQUAU83WW.p8' % file_path

    api = Api('LDQUAU83WW', key_file_path, '69a6de72-64fe-47e3-e053-5b8c7c11a4d1')

    beta_group_ids = [
        '6bf7a45e-8ebf-4bd7-b3af-1e64b0bdaf07',  # myf
        '2d3288c1-1665-43fe-9299-d3cb8b264a32',  # fon
        '94bdf84e-508f-4889-932d-d570597bae7c',  # wlan
        '95f00f2e-d22b-433e-984b-62a9dcacc65a',  # sh
        '75ce8888-e518-4c90-9bec-89518acc945c'  # tv
    ]

    data = []

    # read information
    for beta_group_id in beta_group_ids:
        beta_group = api.read_beta_group_information(beta_group_id)
        beta_testers = api.list_beta_testers(filters={'betaGroups': '%s' % beta_group_id})
        data.append(BetaGroup(beta_group, beta_testers))

    template = loader.get_template('stores/ios_all_inhouse_testers.html')
    context = {
        'title': 'All iOS Inhouse Testers',
        'data': data
    }
    return HttpResponse(template.render(context, request))


def ios_delete_beta_testers(request, id):
    """
    ios all inhouse beta testers page

    :param request: request
    :return: response
    """
    if request.method != 'POST':
        return HttpResponseRedirect('/stores/apps/ios/allInhouseTesters?result=failed')

    file_path = pathlib.Path(__file__).parent.resolve()
    key_file_path = '%s/assets/AuthKey_LDQUAU83WW.p8' % file_path

    api = Api('LDQUAU83WW', key_file_path, '69a6de72-64fe-47e3-e053-5b8c7c11a4d1')

    beta_tester = api.read_beta_tester_information(id)
    api.delete_beta_tester(beta_tester)

    return HttpResponseRedirect('/stores/apps/ios/allInhouseTesters?result=success')