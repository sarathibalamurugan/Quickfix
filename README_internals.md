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

### I4 - Prepared Report
 - real-time reports generates instantly when user hits run. but prepared reports runs and fetch all the data for the report in background. its useful when the data to executed is so large . real-time reports will take much time and the screen will be freez untill the data is generated.
 - the user actually see the outdated report if
 underlying data changes between report preparations . the user should manually re-prepare the report. Because the report reads from stored JSON output.

 ### I5 - Report Builder & Custom Report
 - Report builder is used when there is no custom calculations and no dynamic aggregation logic, No backend processing needed. Script report is used when you need JOINs across multiple DocTypes, need performance-optimized SQL, want dynamic columns and other server side customization. and report builder in a production site is a mistake when it will avoid validations and shows all fields to everyone. it can fetch all records where user dont have access to read.

### J1 - Jinja Print Format: Job Card Receipt
- the language is identified and alterd during the print time. the language passed to the system language setting . the the wrap strings are converted to the specified language. based on the dictionary for translation frappe has. if any string not in the dictionary then it registers as previous lang.
- Putting a frappe.get_all() call inside the Jinja template directly can access the database directly. the pdf fetching may be slowed. and it hard to debug or refactor. while Pre-compute in before_print() and attach to self, then reference in template as
doc.precomputed_field. it is a safe way to access the database while printing or generating pdf. easy to debug , can write testcase, etc,.

### J2 - Raw Print vs HTML to PDF
- Raw printing sends printer control commands directly to the device. there is no HTMl rendering . sending only plain text and control codes. no complex layoout , no images. while in HTML PDF rendering , there is full html rendering. and support images, multi-languages, ect,. 
-  - position: sticky
    - display: flex (advanced flex behaviors)
    - position: fixed (PDF engine may overlap content incorrectly)

-  without doc.get_formatted() the currency value will shown like just integer. but with that it will the currency logo and in float value.

### K1 - Background Jobs: Queues, Timeouts, Progress
Task A - Queue names:
- short - is for small background jobs like sending email, status changing. And it took small amount of time like 300s.
- long - is for large task like data import, report genarating,and any bulk operations.
- default - Its not fast and its not heavy. its for normal regular jobs.

Task D - Job failure handling:
- since I tested it , it fails only once and not rerunned.

###  K2 - Scheduler Events & Cron
- to disable scheduler for a specific site use command `bench --site site-name disable-sheduler`. dev site scheduler is disabled because the scheduled event may trigger any realtime workflow like sending emails, ect,.. to avoiding that kind of side effects. devs disabled it. for the controlled testing.
- If the worker was down the scheduled job will stopped running untill the worker come alive. but the job should not died , if its expires then failed.

### K3 - Performance Engineering 
Task A - N+1 query detection and fix:
```python
  job_cards = frappe.get_all("Job Card", fields=["name","assigned_technician","assigned_technician.technician_name", "assigned_technician.phone"])
    for jc in job_cards:
      print(jc.technician_name, jc.phone)```
```
Task B - Bulk operations:
- it took 0.01 secs to change the status into cancel. and i tried the bulk_insert it took 0.04 seconds to create and insert.

Task C - Indexing:
- 1. primay
  2. creation
  3. amended_from_index
  4. status_index
- you would NOT add a search index to every field. because, they improve reads. but slow down writes. while updating, deleting, inserting anything everytime a tree will be created and slows down.

### L1 - REST Resource API & Custom API
Task A - Resource API (test with curl or Postman):
- GET http://quickfix-dev.localhost:8003/api/resource/Job%20Card
    - {
    "session_expired": 1,
    "data": [
        {
            "name": "JC-2026-00001"
        },
        {
            "name": "JC-2026-00002"
        },
        {
            "name": "JC-2026-00003"
        },
        {
            "name": "JC-2026-00004"
        },
        {
            "name": "JC-2026-00005"
        },
        {
            "name": "JC-2026-00006"
        },
        {
            "name": "JC-2026-00007"
        },
        {
            "name": "JC-2026-00008"
        },
        {
            "name": "JC-2026-00009"
        },
        {
            "name": "JC-2026-00010"
        },
        {
            "name": "JC-2026-00010-1"
        },
        {
            "name": "JC-2026-00012"
        },
        {
            "name": "JC-2026-00013"
        },
        {
            "name": "JC-2026-00013-1"
        },
        {
            "name": "JC-2026-00013-2"
        },
        {
            "name": "JC-2026-00013-3"
        },
        {
            "name": "JC-2026-00013-4"
        },
        {
            "name": "JC-2026-00013-5"
        },
        {
            "name": "JC-2026-00012-1"
        },
        {
            "name": "JC-2026-00015"
        }
    ],
    "_debug_messages": "[\"#### query\\nSELECT `user`,`sessiondata` FROM `tabSessions` WHERE `sid`='d05d24060e876a336a90a8cb1f33e2118e823efeb39433b9cee9f0b7' AND `lastupdate`>'2026-03-12 08:58:50.027459'\\n####\",\"#### query\\nSELECT `user` FROM `tabSessions` WHERE `sid`='d05d24060e876a336a90a8cb1f33e2118e823efeb39433b9cee9f0b7'\\n####\",\"#### query\\nDELETE FROM `tabSessions` WHERE `sid`='d05d24060e876a336a90a8cb1f33e2118e823efeb39433b9cee9f0b7'\\n####\",\"#### query\\ncommit and chain\\n####\",\"#### query\\nSELECT * FROM `tabDocType` WHERE `name`='Job Card' ORDER BY `creation` DESC LIMIT 1\\n####\",\"#### query\\nSELECT * FROM `tabDocField` WHERE `parent`='Job Card' AND `parenttype`='DocType' AND `parentfield`='fields' ORDER BY `idx` ASC\\n####\",\"#### query\\nSELECT * FROM `tabDocPerm` WHERE `parent`='Job Card' AND `parenttype`='DocType' AND `parentfield`='permissions' ORDER BY `idx` ASC\\n####\",\"#### query\\nSELECT * FROM `tabDocType Action` WHERE `parent`='Job Card' AND `parenttype`='DocType' AND `parentfield`='actions' ORDER BY `idx` ASC\\n####\",\"#### query\\nSELECT * FROM `tabDocType Link` WHERE `parent`='Job Card' AND `parenttype`='DocType' AND `parentfield`='links' ORDER BY `idx` ASC\\n####\",\"#### query\\nSELECT * FROM `tabDocType State` WHERE `parent`='Job Card' AND `parenttype`='DocType' AND `parentfield`='states' ORDER BY `idx` ASC\\n####\",\"#### query\\nSELECT * FROM `tabCustom Field` WHERE `dt`='Job Card' ORDER BY `idx` DESC\\n####\",\"#### query\\nSELECT * FROM `tabProperty Setter` WHERE `doc_type`='Job Card' ORDER BY `creation` DESC\\n####\",\"#### query\\nSELECT * FROM `tabCustom DocPerm` WHERE `parent`='Job Card' ORDER BY `creation` ASC\\n####\",\"#### query\\nSELECT * FROM `tabDocType Link` WHERE `parent`='Job Card' AND `custom`=1 ORDER BY `creation` DESC\\n####\",\"#### query\\nSELECT * FROM `tabDocType Action` WHERE `parent`='Job Card' AND `custom`=1 ORDER BY `creation` DESC\\n####\",\"#### query\\nSELECT * FROM `tabDocType State` WHERE `parent`='Job Card' AND `custom`=1 ORDER BY `creation` DESC\\n####\",\"#### query\\nselect table_rows from information_schema.tables where table_name = 'tabJob Card' and table_schema = '_821d9f092809d769'\\n####\",\"#### query\\nSELECT `column_name` FROM `information_schema`.`columns` WHERE `table_name`='tabJob Card'\\n####\",\"#### query\\nSELECT `name` FROM `tabDocType` WHERE `istable`=1\\n####\",\"#### query\\nSELECT `perm_type`,`doc_type` FROM `tabPermission Type` ORDER BY `perm_type` ASC\\n####\",\"#### query\\nSELECT `name` FROM `tabJob Card` LIMIT 20\\n####\",\"#### query\\nselect data from `__UserSettings`\\n\\t\\t\\twhere `user`='Guest' and `doctype`='Job Card'\\n####\"]"
}
- GET http://quickfix-dev.localhost:8003/api/resource/Job%20Card/JC-2026-00023
    - {
    "session_expired": 1,
    "data": {
        "name": "JC-2026-00023",
        "owner": "Administrator",
        "creation": "2026-03-19 11:01:05.629048",
        "modified": "2026-03-19 11:01:18.599825",
        "modified_by": "Administrator",
        "docstatus": 1,
        "idx": 0,
        "customer_name": "asa",
        "customer_phone": "1234567890",
        "device_type": "Laptop",
        "problem_description": "<div class=\"ql-editor read-mode\"><p>lkjhgfdsa</p></div>",
        "assigned_technician": "TECH-0002",
        "estimated_cost": 0.0,
        "priority": "Normal",
        "parts_total": 0.0,
        "labour_charge": 500.0,
        "final_amount": 500.0,
        "payment_status": "Unpaid",
        "status": "Ready for Delivery",
        "doctype": "Job Card",
        "parts_used": []
    },
    "_debug_messages": "[\"#### query\\nSELECT `user`,`sessiondata` FROM `tabSessions` WHERE `sid`='d05d24060e876a336a90a8cb1f33e2118e823efeb39433b9cee9f0b7' AND `lastupdate`>'2026-03-12 09:01:35.957639'\\n####\",\"#### query\\nSELECT `user` FROM `tabSessions` WHERE `sid`='d05d24060e876a336a90a8cb1f33e2118e823efeb39433b9cee9f0b7'\\n####\",\"#### query\\nDELETE FROM `tabSessions` WHERE `sid`='d05d24060e876a336a90a8cb1f33e2118e823efeb39433b9cee9f0b7'\\n####\",\"#### query\\ncommit and chain\\n####\",\"#### query\\nSELECT * FROM `tabJob Card` WHERE `name` = 'JC-2026-00023'\\n####\",\"#### query\\nSELECT * FROM `tabPart Usage Entry`\\n\\t\\t\\tWHERE `parent`= 'JC-2026-00023'\\n\\t\\t\\t\\tAND `parenttype`= 'Job Card'\\n\\t\\t\\t\\tAND `parentfield`= 'parts_used'\\n\\t\\t\\tORDER BY `idx` ASC\\n####\"]"
}
      - POST http://quickfix-dev.localhost:8003/api/resource/Spare%20Part
        - {
    "session_expired": 1,
    "data": {
        "name": "PART-2026-0003",
        "owner": "Guest",
        "creation": "2026-03-19 11:10:41.801788",
        "modified": "2026-03-19 11:10:41.801788",
        "modified_by": "Guest",
        "docstatus": 0,
        "idx": 4,
        "part_name": "Display Laptop glass",
        "part_code": "0011",
        "compatible_device_type": "Laptop",
        "unit_cost": 100.0,
        "selling_price": 150.0,
        "stock_qty": 995.0,
        "reorder_level": 5.0,
        "is_active": 1,
        "doctype": "Spare Part"
    },
    "_debug_messages": "[\"#### query\\nSELECT `user`,`sessiondata` FROM `tabSessions` WHERE `sid`='d05d24060e876a336a90a8cb1f33e2118e823efeb39433b9cee9f0b7' AND `lastupdate`>'2026-03-12 09:10:41.797939'\\n####\",\"#### query\\nSELECT `user` FROM `tabSessions` WHERE `sid`='d05d24060e876a336a90a8cb1f33e2118e823efeb39433b9cee9f0b7'\\n####\",\"#### query\\nDELETE FROM `tabSessions` WHERE `sid`='d05d24060e876a336a90a8cb1f33e2118e823efeb39433b9cee9f0b7'\\n####\",\"#### query\\ncommit and chain\\n####\",\"#### query\\nSELECT `defkey`,`defvalue` FROM `tabDefaultValue` WHERE `parent`='Guest' ORDER BY `creation`\\n####\",\"#### query\\nSELECT `name` FROM `tabDevice Type` WHERE `name`='Laptop' LIMIT 1\\n####\",\"#### query\\nSELECT `name`,`event`,`method` FROM `tabNotification` WHERE `enabled`=1 AND `document_type`='Spare Part' ORDER BY `creation` DESC\\n####\",\"#### query\\nSELECT `name` FROM `tabDocument Naming Rule` WHERE `document_type`='Spare Part' AND `disabled`=0 ORDER BY `priority` DESC\\n####\",\"#### query\\nSELECT `current` FROM `tabSeries` WHERE `name`='PART-2026-' FOR UPDATE\\n####\",\"#### query\\nUPDATE `tabSeries` SET `current` = `current` + 1 WHERE `name`='PART-2026-'\\n####\",\"#### query\\nSELECT `name` FROM `tabWorkflow` WHERE `document_type`='Spare Part' AND `is_active`=1 ORDER BY `creation` DESC LIMIT 1\\n####\",\"#### query\\nINSERT INTO `tabSpare Part` (`name`, `owner`, `creation`, `modified`, `modified_by`, `docstatus`, `idx`, `part_name`, `part_code`, `compatible_device_type`, `unit_cost`, `selling_price`, `stock_qty`, `reorder_level`, `is_active`)\\n\\t\\t\\t\\t\\tVALUES ('PART-2026-0003', 'Guest', '2026-03-19 11:10:41.801788', '2026-03-19 11:10:41.801788', 'Guest', '0', 4, 'Display Laptop glass', '0011', 'Laptop', 100.0e0, 150.0e0, 995.0e0, 5.0e0, 1)\\n####\",\"#### query\\nSELECT `name` FROM `tabNotification Settings` WHERE `name`='Guest' LIMIT 1\\n####\",\"#### query\\nSELECT `module`,`custom`,`is_tree` FROM `tabDocType` WHERE `name`='Notification Settings' ORDER BY `creation` DESC LIMIT 1\\n####\",\"#### query\\nSELECT * FROM `tabNotification Settings` WHERE `name` = 'Guest'\\n####\",\"#### query\\nSELECT * FROM `tabNotification Subscribed Document`\\n\\t\\t\\tWHERE `parent`= 'Guest'\\n\\t\\t\\t\\tAND `parenttype`= 'Notification Settings'\\n\\t\\t\\t\\tAND `parentfield`= 'subscribed_documents'\\n\\t\\t\\tORDER BY `idx` ASC\\n####\",\"#### query\\nSELECT `name` FROM `tabAssignment Rule` WHERE `document_type`='Spare Part' AND `disabled`=0 ORDER BY `priority` DESC\\n####\",\"#### query\\nSELECT `name` FROM `tabAssignment Rule` WHERE `due_date_based_on`<>'' AND `document_type`='Spare Part' AND `disabled`=0\\n####\",\"#### query\\nSELECT `name` FROM `tabDocType` WHERE `name`='Spare Part' LIMIT 1\\n####\",\"#### query\\nSELECT `name` FROM `tabUser` WHERE `name`='Guest' LIMIT 1\\n####\",\"#### query\\nINSERT INTO `tabAudit Log` (`name`, `owner`, `creation`, `modified`, `modified_by`, `docstatus`, `idx`, `doctype_name`, `document_name`, `action`, `user`, `timestamp`)\\n\\t\\t\\t\\t\\tVALUES ('us297iu53v', 'Guest', '2026-03-19 11:10:41.812430', '2026-03-19 11:10:41.812430', 'Guest', '0', 0, 'Spare Part', 'PART-2026-0003', 'on_update', 'Guest', '2026-03-19 11:10:41.812167')\\n####\",\"#### query\\nSELECT `name` FROM `tabMilestone Tracker` WHERE `document_type`='Spare Part' AND `disabled`=0\\n####\"]"
}
- PUT http://quickfix-dev.localhost:8003/api/resource/Spare%20Part/PART-2026-0002
    - {
    "session_expired": 1,
    "data": {
        "name": "PART-2026-0002",
        "owner": "Administrator",
        "creation": "2026-03-03 15:18:25.607487",
        "modified": "2026-03-19 11:47:28.489797",
        "modified_by": "Guest",
        "docstatus": 0,
        "idx": 4,
        "part_name": "Display Mobile",
        "part_code": "00111",
        "compatible_device_type": "Smartphone",
        "unit_cost": 100.0,
        "selling_price": 150.0,
        "stock_qty": 995.0,
        "reorder_level": 5.0,
        "is_active": 1,
        "doctype": "Spare Part"
    },
    "_debug_messages": "[\"#### query\\nSELECT `user`,`sessiondata` FROM `tabSessions` WHERE `sid`='d05d24060e876a336a90a8cb1f33e2118e823efeb39433b9cee9f0b7' AND `lastupdate`>'2026-03-12 09:47:28.485331'\\n####\",\"#### query\\nSELECT `user` FROM `tabSessions` WHERE `sid`='d05d24060e876a336a90a8cb1f33e2118e823efeb39433b9cee9f0b7'\\n####\",\"#### query\\nDELETE FROM `tabSessions` WHERE `sid`='d05d24060e876a336a90a8cb1f33e2118e823efeb39433b9cee9f0b7'\\n####\",\"#### query\\ncommit and chain\\n####\",\"#### query\\nSELECT * FROM `tabSpare Part` WHERE `name` = 'PART-2026-0002' FOR UPDATE\\n####\",\"#### query\\nSELECT * FROM `tabSpare Part` WHERE `name` = 'PART-2026-0002' FOR UPDATE\\n####\",\"#### query\\nSELECT `name` FROM `tabDevice Type` WHERE `name`='Smartphone' LIMIT 1\\n####\",\"#### query\\nUPDATE `tabSpare Part`\\n\\t\\t\\t\\tSET `owner`='Administrator', `creation`='2026-03-03 15:18:25.607487', `modified`='2026-03-19 11:47:28.489797', `modified_by`='Guest', `docstatus`='0', `idx`=4, `part_name`='Display Mobile', `part_code`='00111', `compatible_device_type`='Smartphone', `unit_cost`=100.0e0, `selling_price`=150.0e0, `stock_qty`=995.0e0, `reorder_level`=5.0e0, `is_active`=1 WHERE `name`='PART-2026-0002'\\n####\",\"#### query\\nSELECT `name` FROM `tabDocType` WHERE `name`='Spare Part' LIMIT 1\\n####\",\"#### query\\nSELECT `name` FROM `tabUser` WHERE `name`='Guest' LIMIT 1\\n####\",\"#### query\\nINSERT INTO `tabAudit Log` (`name`, `owner`, `creation`, `modified`, `modified_by`, `docstatus`, `idx`, `doctype_name`, `document_name`, `action`, `user`, `timestamp`)\\n\\t\\t\\t\\t\\tVALUES ('kdk1inliu6', 'Guest', '2026-03-19 11:47:28.494124', '2026-03-19 11:47:28.494124', 'Guest', '0', 0, 'Spare Part', 'PART-2026-0002', 'on_update', 'Guest', '2026-03-19 11:47:28.493303')\\n####\"]"
}
- DELETE http://quickfix-dev.localhost:8003/api/resource/Spare%20Part/PART-2026-0003
    - {
    "session_expired": 1,
    "data": "ok",
    "_debug_messages": "[\"#### query\\nSELECT....
    }

Task B - Token Authentication (API key + secret):
- Session cookie Auth - server create a session for the user. user have to login via method. browser stores SID cokies and uses CSRF protection for every request. best for UI based uses.
- Token Auth - no session is stored and no login endpoint needed. only api key and secret key is used for every request. no cookies and csrf used. best for server-to-server communication. 

Task D - Rate limiting & abuse protection:
- allow_guest=True endpoint leads to get attacks by unknown attackers. attacks like Enumeration attacks, DoS Attacks and Data scraping.

### L2 - Webhooks: Outgoing & Incoming
Task B - Incoming Webhook Endpoint:
- == searches in expected time interval, so attackers can analyze the time duration and can find the correct hmac. to overcome this hmac.compare_digest is used . it uses constant time interval where attacker cant guess the timing.
- If a duplicate payment is sent the audit log is checked for duplication . if duplicate found logic stops.
