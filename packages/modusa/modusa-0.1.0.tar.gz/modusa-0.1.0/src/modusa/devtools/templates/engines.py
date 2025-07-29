#!/usr/bin/env python3


from modusa import excp
from modusa.decorators import validate_args_type
from modusa.engines.base import ModusaEngine
from typing import Any

class {class_name}(ModusaEngine):
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
	
	
	@validate_args_type()
	def run(self) -> Any:
		pass