### B2 - ORM Internals & Query Builder (12 pts)
 Part A - Table naming
 - In [1]: frappe.db.sql("SHOW TABLES LIKE '%Job%'")
- Out[1]: (('tabJob Card',), ('tabScheduled Job Log',), ('tabScheduled Job Type',))
 - the tab prefix ccenvention is a naming method in frappe for sql tables considering all doctypes.

  - frappe.db.sql("DESCRIBE `tabJob Card`", as_dict=True)
  - i dont have any fields because the fields setup are in upcoming steps. i see name, creation, modified, modified_by, owner, docstatus.

### C3 - Renaming task
- Yes the assigned_technician name changed in the job card too. because when using the rename document feature. it find all references in the DB and changes it automatically. the track changes is tracking the changes in the record like renaming , value change in any field . it will log everything by tracking it.
- 