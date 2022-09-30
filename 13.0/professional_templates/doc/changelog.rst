.. _changelog:

Changelog
=========



`Version 2.1.0 (Tue Oct 20 04:24:05 2020)`
--------------------------------------------
- `[IMP] Sales Order Reports`
    - Added Optional Products section in sales order reports templates.
- `[IMP] table css class`
  - removed `table-condensed` and replaced with `table-sm`.

`Version 2.0.2 (Mon Oct  5 03:25:27 2020)`
--------------------------------------------
- `[FIX] Customer Reference`
    - Added the missing costomer reference field to the  `delivery note` templates.

`Version 2.0.1 (Wed Sep 16 10:50:51 2020)`
--------------------------------------------
- `[FIX] unwanted table border`
    - unwanted table border line was removed in the `picking_lines` template.

`Version 2.0.0 (Tue Sep 15 01:25:15 2020)`
--------------------------------------------
- `[IMP] full multi-company behaviour:`
    - the letterhead is now company-dependent. If you switch company the letter head is also switched unlike before.
- `[IMP] Letterhead limited:`
    - the letterhead is now limited to Odoo reports covered by professional_templates.


`Version 1.7 (Tue Apr 14 05:13:27 2020)`
--------------------------------------------
- `[IMP] Account invoice templates:`
    - General improvements on the templates for invoice and removal of redundant templates

`Version 1.6 (Sat Mar 28 00:36:07 2020)`
--------------------------------------------
- `[FIX] Account invoice`:
    - Reference  field  added to all invoice templates `o.ref`


`Version 1.5 (Sat Mar  3 16:02:30 2020)`
--------------------------------------------
- `[FIX] Stock Picking`:
    - Renamed field `weight_uom_id`  to `weight_uom_name`

`Version 1.4 (Sat Feb  1 00:33:39 2020)`
--------------------------------------------
- `[IMP] Account Journal`:
    - Brought back `display_on_footer` field for bank accounts

`Version 1.3 (Thu Jan  9 12:47:38 2020)`
--------------------------------------------
- [FIX] Issue where company address text in not wrapping when long
- [FIX] Issue where the watermark PDF delete button is blocked by text and cannot be clicked when one is already uploaded

`Version 1.2 (Wed Dec 25 17:51:56 2019)`
--------------------------------------------
- [FIX] Odoo Studio issue found when trying to edit invoice and sales order reports.

`Version 1.1 (Thu Dec 19 01:06:45 2019)`
--------------------------------------------
- [FIX] amount in words singleton error has been fixed.

`Version 1.0 (Fri Dec 06 22:33:08 2019)`
--------------------------------------------
- Stable Relase for Odoo 13.0
- [FIX] in website, Error print or download invoice

`Version 0.1 (beta) (Fri Nov 15 04:33:08 2019)`
--------------------------------------------------
- New module for Odoo 13.0 ported from the same module for odoo 12.0 with same features and settings
