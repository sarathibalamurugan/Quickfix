### B2 - ORM Internals & Query Builder (12 pts)
 Part A - Table naming
 - In [1]: frappe.db.sql("SHOW TABLES LIKE '%Job%'")
- Out[1]: (('tabJob Card',), ('tabScheduled Job Log',), ('tabScheduled Job Type',))
 - the tab prefix ccenvention is a naming method in frappe for sql tables considering all doctypes.

  - frappe.db.sql("DESCRIBE `tabJob Card`", as_dict=True)
  - i dont have any fields because the fields setup are in upcoming steps. i see name, creation, modified, modified_by, owner, docstatus.

### C1 - Child table internals.
- when saving the JC after appending the part_used row , the frappe automatically added part, part_name, unit_price, quantity. and the others are idx, name, doctype, owner, parent,parentfield, parenttype.
- DB table name for the Part Usage Entry DocType is `tabPart Usage Entry`.
-  the idx is also changed after the deleted row. and continues from the previous one from the deleted row.

### C3 - Renaming task
- Yes the assigned_technician name changed in the job card too. because when using the rename document feature. it find all references in the DB and changes it automatically. the track changes is tracking the changes in the record like renaming , value change in any field . it will log everything by tracking it.
- setting a field as "unique" in the DocType is that it dont insert the duplicates. every time the record creates it creates unique index in the database. while frappe.db.exists() in validate is checks after create the index it may return dublicate indices.

### D1 - Roles, Permission Matrix, Document Sharing
- If a non-manager calls the frappe.only_for("QF Manager") it doesnt allow them to continue to execute the remining codes.
- After used frappe.get_doc_permissions(doc) by logging in another user i got : 
- {'if_owner': {},
 'has_if_owner_enabled': False,
 'select': 0,
 'read': 1,
 'write': 1,
 'create': 0,
 'delete': 0,
 'submit': 1,
 'cancel': 0,
 'amend': 0,
 'print': 0,
 'email': 0,
 'report': 1,
 'import': 0,
 'export': 1,
 'share': 1}

### j