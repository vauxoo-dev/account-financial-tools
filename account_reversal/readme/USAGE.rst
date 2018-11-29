If you select an entry from Invoicing > Adviser > Journal Entries,
then an action menu 'Reverse Entries' is available. If clicked, then a wizard
allows user to select Reversal Date, Reversal Journal, Prefix, Post and Reconcile.

* If no Reversal Journal is selected, then the same journal is used
* If Post is True, then reversal entry will be posted else it will be leaved
  as a draft entry.
* If Post and Reconcile are True, then all entry lines with reconciled accounts
  of the entry will be reconciled with the reserval entry ones.

There is also a new menu Invoicing > Adviser > Journal Entries to be Reversed
in order to allow tracking entries that must be reserved for any reason.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/92/11.0

