from django.urls import path
from . import views
from . import views_schedule_account

urlpatterns = [
    path("save/", views.save_listing, name="save_listing"),
    path("start/", views.start_publishing, name="start_publishing"),
    path("get-latest/", views.get_latest_listing, name="get_latest_listing"),
    path("save-credentials/", views.save_credentials, name="save_credentials"),
    path("get-credentials/", views.get_credentials, name="get_credentials"),
    path("debug-data/", views.debug_data, name="debug_data"),

    # New automation handlers
    path("renew/", views.run_renew_listings, name="run_renew"),
    path("relist/", views.run_relist_ads, name="run_relist"),
    path("delete-duplicates/", views.run_delete_duplicates, name="run_delete_duplicates"),
    path("delete-all/", views.run_delete_all, name="run_delete_all"),
    path("delete-drafts/", views.run_delete_drafts, name="run_delete_drafts"),
    path("open-link/", views.run_open_custom_link, name="run_open_link"),

    # Scheduling
    path("schedule/create/", views_schedule_account.create_schedule, name="create_schedule"),
    path("schedule/list/", views_schedule_account.get_schedules, name="get_schedules"),
    path("schedule/<int:schedule_id>/pause/", views_schedule_account.pause_schedule, name="pause_schedule"),
    path("schedule/<int:schedule_id>/resume/", views_schedule_account.resume_schedule, name="resume_schedule"),
    path("schedule/<int:schedule_id>/delete/", views_schedule_account.delete_schedule, name="delete_schedule"),
    path("schedule/stats/", views_schedule_account.get_schedule_stats, name="schedule_stats"),

    # Account management
    path("account/add/", views_schedule_account.add_account, name="add_account"),
    path("account/list/", views_schedule_account.get_all_accounts, name="list_accounts"),
    path("account/active/", views_schedule_account.get_active_accounts, name="active_accounts"),
    path("account/available/", views_schedule_account.get_available_account, name="available_account"),
    path("account/<int:account_id>/", views_schedule_account.get_account_details, name="account_details"),
    path("account/<int:account_id>/status/", views_schedule_account.update_account_status, name="update_account_status"),
    path("account/<int:account_id>/delete/", views_schedule_account.delete_account, name="delete_account"),
    path("account/<int:account_id>/health/", views_schedule_account.get_account_health, name="account_health"),
    path("account/rotate/", views_schedule_account.rotate_account, name="rotate_account"),
    path("account/pool/stats/", views_schedule_account.get_pool_stats, name="pool_stats"),
    path("account/pool/health/", views_schedule_account.get_pool_health_report, name="pool_health"),
]
