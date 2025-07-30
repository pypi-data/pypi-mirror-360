
==============
 Installation
==============


Prerequisites
-------------

You'll need Python >= 3.8, and a database.  See also
the Wutta docs:

* :doc:`wuttjamaican:narr/install/prereqs`
* :ref:`wuttjamaican:create-appdb`

But for convenience here is a cheat sheet:

*PostgreSQL*

.. code-block:: sh

   sudo apt install build-essential python3-dev python3-venv postgresql libpq-dev

   sudo -u postgres createuser sideshow
   sudo -u postgres psql -c "ALTER USER sideshow PASSWORD 'mypassword'"
   sudo -u postgres createdb -O sideshow sideshow

*MySQL*

.. code-block:: sh

   sudo apt install build-essential python3-dev python3-venv default-mysql-server

   sudo mysql -e "CREATE USER sideshow@localhost"
   sudo mysql -e "ALTER USER sideshow@localhost  IDENTIFIED BY 'mypassword'"
   sudo mysqladmin create sideshow
   sudo mysql -e "GRANT ALL ON sideshow.* TO sideshow@localhost"


Virtual Environment
-------------------

You should use a separate Python virtual environment for Sideshow.
See also :doc:`wuttjamaican:narr/install/venv` but these docs will
assume this exists at ``/srv/envs/sideshow``.

Note that root privileges are required to create the folder, but then
the folder ownership should be changed to whatever you need:

.. code-block:: sh

   cd /srv/envs
   sudo mkdir -p sideshow
   sudo chown myname:myname sideshow

   python3 -m venv /srv/envs/sideshow
   cd /srv/envs/sideshow
   source bin/activate


Install Sideshow
----------------

First install the Sideshow package to your virtual environment.  Note
that you must specify which DB backend to use:

.. code-block:: sh

   # postgres
   bin/pip install Sideshow[postgres]

   # mysql
   bin/pip install Sideshow[mysql]

Then you can run the Sideshow installer:

.. code-block:: sh

   bin/sideshow install

That will prompt you for DB connection info etc.  When finished you
can run Sideshow:

.. code-block:: sh

   bin/wutta -c app/web.conf webapp
