# The slug of the panel to be added to HORIZON_CONFIG. Required.
PANEL = 'notifications'
# The slug of the dashboard the PANEL associated with. Required.
PANEL_DASHBOARD = 'management'
# The slug of the panel group the PANEL is associated with.
PANEL_GROUP = 'default'

# Python panel class of the PANEL to be added.
ADD_PANEL = 'adjutant_ui.content.notifications.panel.NotificationPanel'

ADD_INSTALLED_APPS = [
    'adjutant_ui.content.notifications'
]
