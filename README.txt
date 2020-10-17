============================================================================================
Odoo generateDS plugin: generate Odoo asbtract model mixins and fields from your xsd schemas
============================================================================================

This plugin has been developped by Raphaël Valyi from Akretion and was derived from
the official Django generateDS plugin that is documented here:
http://www.davekuhlman.org/generateDS.html#django-generating-models-and-forms

This Odoo plugin generate only models. Odoo is able to generate views dynamically alone
and we also made the dedicated spec_driven_model Odoo module to help with views.
You can read how it evolved from the Django plugin by looking at the commits log.

Disclaimer: we know this code doesn't really look like modern Python. But this is
an assumed choice: we prefer not changing the code too much from the original Django
plugin so if generateDS evolves it will be easier to follow the changes here.

Although, there are likely other configurations that will work, one
reasonably simple way is the following:


1. Install generateDS::

       $ pip install generateDS

1. Download the source distribution of generateds-odoo with the
   following::

       $ git clone https://github.com/akretion/generateds-odoo

2. Change directory to the ``django`` directory (i.e. the directory
   containing this file)::

       $ cd generateds/django

3. In that directory, either, (a) create, a symbolic link to
   ``generateDS.py``::

       $ ln -s ../generateDS.py

   Or, (b) copy ``generateDS.py`` to that directory::

       $ cp ../generateDS.py .

4. In that directory, Run ``gends_run_gen_odoo.py``.  For
   example::

       $ # Brazilian electronic invoice:
       $ python3 gends_run_gen_odoo.py -f -l nfe -x 4_00 -e '^ICMS\d+|^ICMSSN\d+' -d . -v /tmp/generated/schemas/nfe/v4_00/leiauteNFe_v4.00.xsd
       $
       $ # UBL 2.3 invoice:
       $ python3 gends_run_gen_odoo.py -f -l ubl -x 23 -d . -v /home/rvalyi/DEV/UBL-2.3/xsd/maindoc/UBL-Invoice-2.3.xsd

If the above ran successfully, it should have created these files::

    leiauteNFe_v400lib.py
    UBL-Invoice-23lib.py


.. vim:ft=rst:
