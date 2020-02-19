Configuring Adjutant-UI
=======================

Adjutant-ui relies on the ``OPENSTACK_ADJUTANT_URL`` setting, as much
like Keystone's url, this is needed before the user is authenticated and a
valid catalog has been returned. This url is used for the password reset
functionality, and signup if that panel is turned on.

.. code-block:: python

  OPENSTACK_ADJUTANT_URL = "http://127.0.0.1:5050/v1"


Beyond that all the other settings are optional, with reasonably sensible
defaults.

Username is email
+++++++++++++++++

The first major setting to consider, and this needs to match the same one in
Adjutant, is ``USERNAME_IS_EMAIL``. This defaults to ``True`` but can be
changed. In doing so all the username/email related forms are updated to
reflect the change.

.. code-block:: python

  USERNAME_IS_EMAIL = False


Quota settings
++++++++++++++

If you are using or have enabled the quota management in Adjutant and the UI
then there are some settings around that which you can tweak.

``IMPORTANT_QUOTAS`` lets you change which quota values are emphasised in the
quota update view. Defaults to:

.. code-block:: python

  IMPORTANT_QUOTAS = {
      'nova': [
           'instances', 'cores', 'ram',
      ],
      'cinder': [
          'volumes', 'snapshots', 'gigabytes',
      ],
      'neutron': [
           'network', 'floatingip', 'router', 'security_group',
      ],
      'octavia': [
           'load_balancer',
      ],
  }

``HIDDEN_QUOTAS`` lets you hide quotas that you do not want your users to see
or that you think are redundant and confusing. Defaults to:

.. code-block:: python

  HIDDEN_QUOTAS = {
      # these values have long since been deprecated from Nova
      'nova': [
          'security_groups', 'security_group_rules',
          'floating_ips', 'fixed_ips',
      ],
      # these by default have no limit
      'cinder': [
          'per_volume_gigabytes', 'volumes_lvmdriver-1',
          'gigabytes_lvmdriver-1', 'snapshots_lvmdriver-1',

      ],
      'neutron': [
          'subnetpool',
      ],
  }


Role Translation Settings
+++++++++++++++++++++++++

``ROLE_TRANSLATIONS`` lets you control the way we rename roles in the dashboard
in the Adjutant panels. This is mostly so that you can give your roles simple
names in Keystone, but here in the GUI given them more descriptive or user
friendly names. Defaults to:

.. code-block:: python

  ROLE_TRANSLATIONS = {
      'project_admin': _('Project Administrator'),
      'project_mod': _('Project Moderator'),
      '_member_': _('Project Member'),
      'Member': _('Project Member'),
      'heat_stack_owner': _('Heat Stack Owner'),
      'project_readonly': _('Project Read-only'),
      'compute_start_stop': _('Compute Start/Stop'),
      'object_storage': _('Object Storage')
  }


Service Translation Settings
++++++++++++++++++++++++++++

``SERVICE_TRANSLATIONS`` lets you control the way we rename services from their
service name, to their service type in a friendly manner. This is because most
users do not need to know what the name of the service is, just what the
service type is. Defaults to:

.. code-block:: python

  SERVICE_TRANSLATIONS = {
      'cinder': _('Volume'),
      'neutron': _('Networking'),
      'nova': _('Compute'),
      'octavia': _('Load Balancer'),
  }
