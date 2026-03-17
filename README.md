

### A2: 
- Each site config files are used to config each sites. which have their own db host name, password, user name and db type. while the common site config file is used to config basic common things for client and DB for connection and for data caching , ect,. If we break anything from common site config then the whole bench will collapse. and if we accidentally put secret in the common config like secret key. then the secret key is accessible in all sites for bench level.

- web - handles http requests

    worker- handles backround jobs

    scheduler - handles scheduled events

    Socketio - communication

- If a worker stops, the running backgground job will fail and the waiting jobs in the queue will run when the worker start working again.

### B1:
- /api/method/quickfix.api.get_job_summary is a whitelist function and api rules are setted in api section v1.py and v2.py then it imported to the handle function in `__init__.py` where frappe route to the page.

- /api/resource/Job Card/JC-2024-0001 it will retrurn the object of the resource mentioned. just like method this also called in app.py -> frappe.api.handle(). difference of these two is one is calling a whitelist fuction and another return the objects ir values.

- /track-job will track the fuction only, in frappe.website.serve.get_response().


- x-frappe-csrf-token - 
08419c8e0a6e395ef4208c91cce2765766eea47c1969da1995082bef. we can find this in networks tab after a POST request. if we ommit this token . there is a validate function named validate_csrf_token in frappe.auth.HTTPRequst it wil return nothing.

- frappe.session contains logged_in_user, user, user_email, user_fullname.

- With developer_mode: 1 when triggering an exception the error logs won't create . With developer_mode: 0 the error logs will create. because when in production site the developers cant see the real time errors thats why the errors are saved in the error logs. and also a text like "Using this console may allow attackers to impersonate you and steal your information. Do not enter or paste code that you do not understand." shown in the browser console in production site.


