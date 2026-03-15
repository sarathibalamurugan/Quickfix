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

### D2
-  frappe.get_all will return all the records that the session user dont have access to read. but frappe.get-list will return only the user have access to read with using permission_query_conditions.

### E1 - Complete Job Card Lifecycle
- on_update() - calling self.safe() gave "maximum recursion depth exceeded" error. because while updating if we call self.safe() it will the on_update function again and again. Thats why we are encountering this error.

### E2 - autoname & Renaming
- frappe.rename_doc renamed the technician and all other doctyoe fileds linked to that particular technician's new name. the function calls the rename_doc.py function from the model, where they handled all validates and linked docs.
- merge=False can prevent combining 2 docs having the same name as single doc. if we write merge=True the old doc will be deleted and the another doc with the same name is referenced in all linked docs.

### E3 -  Standard Controller Pattern & override_doctype_class
Part-B
- override_doctype_class can change the core logic if we mentions and validates it. but doc_events run only when the event triggers.

Part-C
- I would choose frappe.db.get_value because for Quickfix Setting Doctype no one have any permission to read. If any validation or controller uses Quickfix Settings field value . they cant access unless using frappe.db.get_value.

### F1 - doc_events: Wildcard, Multiple Handlers, Order
Part-B  Multiple handler conflict:
- First it went for the override doctype class by super.validate() and goes straight to the main controller. the first one runs is controller. I pointed the same validate function in the doc_events too. but the controller validate runs first.
- when you register "*" AND a specific DocType handler for the same event both register run successfully. but if the register have frappe.throw, the first one will run then stops running after throwing error. then the second one fails to run.

### F3 - Asset, Jinja & Website Hooks
Asset hooks
- app_include_js is used when the app documents needs extra features . it's like overriding js file only for the desk apps. and the web_include_js is used to load js files for public website from the app.
- Doctype like Chart Of Accounts use tree view because of the need of hierarchical view. will make you understand of the parent and child level doctypes and docs.
- build cache-busting: is nothing but it used to update the browser cached files to the latest files. It will give you the latest version of the UI instead of cached one.

Jinja hooks:
- Jinja context available in Print Formats can automatically fetch the document and its object. but in web pages, the jinja templates are manually configured.

### F4 - override_whitelisted_methods Hook
- override_whitelisted_methods is used in the hooks and it is reversible and visible used to override whitelist methods whithout touching the file. but monkey patching is something we use at import time , the value is changed at the import time. but cant find out where its used and when used.
-If TWO apps both register override_whitelisted_methods for the same
method only one will win which is the last one based on the of the two apps loaded. the last one  wins.
- When the whitelisted method recieves more number of arguments than it has. or missing something it has, or wrong parameter names leads to the TypeError.
- if your Custom Field has the same fieldname as a field added by a future Frappe update patches may crash and migration may fail.
- if Patch 1 creates a Custom Field and Patch 2 reads it, rollbacking may be dangerous, and re-runnnig become unsafe if they merged in single patch. if they are in separate patch , if one succeed and one fail. the failed one will be re-runned. if they are in single patch re-runnig can leads to duplication.

### G1 - Safe Monkey Patch with Version Guard
Analysis
- _qf_patched guard for to prevent patching twice.
- scattering them in __init__.py is dangerous because debugging it will more harder. and it is hard to track in init. but in monkey patch everything is in single place. but still risky.
- doc_events first - then override_doctype_class - then override_whitelisted_methods - then monkey patch. This is the order because in each step the risk iis increased.

### H1 - Job Card Form Script
- Making a frappe.call inside the validate client event will not work because frappe.call is an asynchronous call and validate is synchnous. validate() finishes quickly and doesn't wait async calls. then the api will response later.
- for async data fetches using refresh is complex. it will run everytime the doc is refreshed, load, save, submit. but in onload, it will run only once. so onload is better than refresh here.

### H3 - List View & Tree View
- Tree DocType is a hierarchy based structure for doctypes which enables is_tree . like parent-child level.
- doctype_tree_js is like doctype_list_js but for tree structure. extra fields like parent_field, is_group are required for the tree js.

### Client Script DocType vs Shipped JS
- Client script doctype used to write js in a doctype and also override app js. client script only stores in the db not in the local or app. when migrating or reinstalling the client scripts will be gone. we have to export it. it can be used for any instant fix needs.
- hiding the field just in UI using js will actually hide the data but in backend the data is still accessible. permission security pitfall can block the user if he doesn't have permission to read it in permission level and after he can't access it using api calls. 

### I1 - Query Report with SQL Safety
-  f-string SQL is dangerous because it can be user to inject sql. if someone changed the f string value to like deleting records, It's highly risk. but using parameterized pattern the SQL all the values as data not the raw SQL. so the SQL is safe here.
