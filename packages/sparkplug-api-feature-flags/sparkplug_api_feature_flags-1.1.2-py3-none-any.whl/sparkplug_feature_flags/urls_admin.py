from django.urls import include, path

from .views import admin as views

app_name = "sparkplug_feature_flags_admin"

uuid_patterns = [
    path(
        "give-access/",
        views.GiveAccessView.as_view(),
        name="give_access",
    ),
    path(
        "remove-access/",
        views.RemoveAccessView.as_view(),
        name="remove_access",
    ),
    path(
        "set-enabled/",
        views.SetEnabledView.as_view(),
        name="set_enabled",
    ),
    path(
        "",
        views.DetailView.as_view(),
        name="detail",
    ),
]

urlpatterns = [
    path(
        "autocomplete/",
        views.AutocompleteView.as_view(),
        name="autocomplete",
    ),
    path(
        "search/",
        views.SearchView.as_view(),
        name="search",
    ),
    path(
        "<str:uuid>/",
        include(uuid_patterns),
    ),
    path(
        "",
        views.ListView.as_view(),
        name="list",
    ),
]
