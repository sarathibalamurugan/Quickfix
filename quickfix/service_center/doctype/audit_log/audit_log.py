# Copyright (c) 2026, Parthsarathi and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AuditLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		action: DF.Data | None
		doctype_name: DF.Link | None
		document_name: DF.Data | None
		timestamp: DF.Datetime | None
		user: DF.Link | None
	# end: auto-generated types

	pass
