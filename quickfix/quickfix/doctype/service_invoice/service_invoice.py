# Copyright (c) 2026, Parthsarathi and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ServiceInvoice(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		name1: DF.Data | None
	# end: auto-generated types

	pass
