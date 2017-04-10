# The name of the dashboard to be added to HORIZON['dashboards']. Required.
DASHBOARD = 'forgot_password'

# A list of applications to be added to INSTALLED_APPS.
ADD_INSTALLED_APPS = [
    'stacktask_ui.dashboards.forgot_password_dash',
    'stacktask_ui.content.forgot_password',
    'overextends',
]
