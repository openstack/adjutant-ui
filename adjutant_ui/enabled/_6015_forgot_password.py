# The name of the dashboard to be added to HORIZON['dashboards']. Required.
DASHBOARD = 'forgot_password'

# A list of applications to be added to INSTALLED_APPS.
ADD_INSTALLED_APPS = [
    'adjutant_ui.dashboards.forgot_password_dash',
    'adjutant_ui.content.forgot_password',
    'overextends',
]
