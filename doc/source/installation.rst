Installation instructions
=========================

Begin by cloning the Horizon and Adjutant UI repositories::

    git clone https://github.com/openstack/horizon
    git clone https://github.com/catalyst/adjutant-ui

Create a virtual environment and install Horizon dependencies::

    cd horizon
    python tools/install_venv.py

Set up your ``local_settings.py`` file::

    cp openstack_dashboard/local/local_settings.py.example openstack_dashboard/local/local_settings.py

Open up the copied ``local_settings.py`` file in your preferred text
editor. You will want to customize several settings:

-  Verify that the ``OPENSTACK_KEYSTONE_URL`` is correct for your environment.
-  ``OPENSTACK_ADJUTANT_URL`` should also be configured to point to your
   Adjutant server and version.

You will also need to update the ``keystone_policy.json`` file in horizon with
the following lines::

    "project_mod": "role:project_mod",
    "project_admin": "role:project_admin",
    "project_mod_or_admin": "rule:admin_required or rule:project_mod or rule:project_admin",
    "project_admin_only": "rule:admin_required or rule:project_admin",
    "identity:project_users_access": "rule:project_mod_or_admin",

Install Adjutant UI with all dependencies in your virtual environment::

    tools/with_venv.sh pip install -e ../adjutant-ui/

And enable it in Horizon::

    cp ../adjutant-ui/enabled/_* openstack_dashboard/local/enabled
