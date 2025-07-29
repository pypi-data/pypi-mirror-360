#!/usr/bin/env python3


from modusa.decorators import validate_args_type
from modusa.generators.base import ModusaGenerator


class {class_name}(ModusaGenerator):
	"""

	"""
	
	#--------Meta Information----------
	name = ""
	description = ""
	author_name = "{author_name}"
	author_email = "{author_email}"
	created_at = "{date_created}"
	#----------------------------------
	
	def __init__(self):
		super().__init__()
	
	
	def generate(self) -> Any:
		pass