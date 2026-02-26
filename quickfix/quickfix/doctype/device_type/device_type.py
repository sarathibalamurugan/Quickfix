# Copyright (c) 2026, Parthsarathi and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DeviceType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		average_repair_hours: DF.Int
		description: DF.SmallText | None
		device_type: DF.Data
	# end: auto-generated types

	pass
