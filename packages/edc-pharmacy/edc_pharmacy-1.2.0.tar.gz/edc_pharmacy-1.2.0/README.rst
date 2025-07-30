|pypi| |actions| |codecov| |downloads|

edc-pharmacy
------------
EDC pharmacy is a simple pharmacy module for randomized control trials that can be integrated into clinicedc/edc projects.

The module includes stock management to enable a research project team to track chain-of-custody of investigational product from a central site to each research site and finally to each patient.
Stock items are physically labeled using the integrated labelling functionality. Generated labels use a randomly generated stock code and code128 barcodes. Label formats are fully customizable.

When integrated with an clinicedc/edc project, study site requests for stock can be generated using the subject's randomization assignment, followup schedule, and prescription.

Installation
============

.. code-block:: bash

    pip install edc_pharmacy

More likely, ``edc_pharmacy`` is installed as a requirement of a ``clinicedc/edc`` project.


Overview
========
Concepts
++++++++

Task at Central

* order (central)
* receive, label as bulk stock, confirm
* repack/decant, label as stock, confirm
* with site stock request, allocate to subject, label for subject
* transfer stock to site

Tasks at Site

* generate stock request PRN (site)
* receive physical stock at site, confirm transfered stock at site
* dispense to clinic/patient
* confirm dispense to patient on CRF

Also:

* medication
* formulation
* prescription

Features
++++++++

* Tracks lot# with randomization assignment
* prints code128 label sheets (py_labels2, django_pylabel, edc_pylabel)
* generates a stock request based on subjects with valid prescriptions (Rx) using the next scheduled visit (see edc_appointment, edc_visit_tracking, edc_visit_schedule)
* stock are created in data but only available if confirmed by scanning barcode into system.


Details
=======

Qty vs Unit QTY
+++++++++++++++

* QTY is the container count, e.g. 5 bottles of 128 tablets.
* UNIT_QTY is the total number of items in the container. A bottle of 128 has ``unit_qty`` of 128 and a ``qty`` of 1.
* All stock items start with a ``qty_in`` =1 and ``qty_out`` =0 while the ``unit_qty`` = ``qty_in`` * ``container.qty`` or as in the example above, ``unit_qty`` = 1 * 128 = 128.
* If the ``unit_qty_out`` equals the initial ``unit_qty_in``, e.g 128==128, the ``qty_out`` is set to 1. A stock item with ``qty_in`` =1 and ``qty_out`` =1 is not available / in stock.

Orders
++++++
Track orders of IMP by recording the LOT # and expiration date.

Repack/Decant
+++++++++++++

Create new stock from an existing stock item. The container of the new stock item cannot be the same as the source container.
For example, create bottles of 128 tabs from a single bulk barrel of tablets.


User Testing
============

Watermarks
++++++++++

Print a watermark on labels during UAT deployments

.. code-block:: python

    EDC_PHARMACY_LABEL_WATERMARK_WORD = "DO NOT USE"

See also `pylabels2 <https://github.com/erikvw/pylabels2>`__.

Print watermark on reports during UAT deployments

.. code-block:: python

    EDC_PDF_REPORTS_WATERMARK_WORD = "SAMPLE"
    EDC_PDF_REPORTS_WATERMARK_FONT = ("Helvetica", 100)

See also `edc-pdf-reports <https://github.com/clinicedc/edc-pdf-reports>`__.


.. |pypi| image:: https://img.shields.io/pypi/v/edc-pharmacy.svg
   :target: https://pypi.python.org/pypi/edc-pharmacy

.. |actions| image:: https://github.com/clinicedc/edc-pharmacy/actions/workflows/build.yml/badge.svg
   :target: https://github.com/clinicedc/edc-pharmacy/actions/workflows/build.yml

.. |codecov| image:: https://codecov.io/gh/clinicedc/edc-pharmacy/branch/develop/graph/badge.svg
   :target: https://codecov.io/gh/clinicedc/edc-pharmacy

.. |downloads| image:: https://pepy.tech/badge/edc-pharmacy
   :target: https://pepy.tech/project/edc-pharmacy
