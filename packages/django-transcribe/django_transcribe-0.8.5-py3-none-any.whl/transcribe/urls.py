from django.conf import settings as django_settings
from django.conf.urls.static import static
from django.urls import include, path
from transcribe.views import reports, web

handler404 = 'transcribe.views.web.display404'
handler500 = 'transcribe.views.web.display500'

project_views = [
    path('', web.landing_page, name='landing_page'),
    path('help/', web.help, name='help'),
    path('faq/', web.faq, name='faq'),
    path('dashboard/', web.DashboardView.as_view(), name='dashboard'),
    path(
        'dashboard/all_tasks/',
        web.DashboardView.as_view(),
        name='dashboard_all_tasks',
        kwargs={'all_tasks': 'all_tasks'},
    ),
    path('projects/', web.ProjectListView.as_view(), name='projects_list'),
    path(
        'project/<int:pk>/',
        web.ProjectDetailView.as_view(),
        name='project_detail',
    ),
    path(
        'project/<int:pk>/download.<str:type>',
        web.ProjectDownloadView.as_view(),
        name='project_download',
    ),
    path(
        'project/<int:pk>/claim/<str:type>/',
        web.ProjectClaimTaskView.as_view(),
        name='project_claim_task',
    ),
    path(
        'userpreferences/<int:pk>/update/',
        web.UserPreferencesUpdateView.as_view(),
        name='user_preferences_update',
    ),
    path(
        'userprojectpreferences/<int:pk>/update/',
        web.UserProjectPreferencesUpdateView.as_view(),
        name='user_project_preferences_update',
    ),
    path(
        'task/<int:pk>/', web.UserTaskUpdateView.as_view(), name='task_workon'
    ),
]

report_views = (
    [
        path('', reports.reports_list, name='list'),
        path('projects/', reports.projects_report, name='projects_report'),
        path('users/', reports.users_report, name='users_report'),
    ],
    'reports',
)

urlpatterns = [
    path('', include(project_views)),
    path('reports/', include(report_views)),
]

if django_settings.DEBUG:
    urlpatterns += static(
        django_settings.STATIC_URL, document_root=django_settings.STATIC_ROOT
    )
