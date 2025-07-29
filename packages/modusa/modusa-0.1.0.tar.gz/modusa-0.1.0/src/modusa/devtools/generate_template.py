#!/usr/bin/env python3

from datetime import date
from pathlib import Path
import questionary
import sys

ROOT_DIR = Path(__file__).parents[3].resolve()
TEMPLATES_DIR = ROOT_DIR / "src/modusa/devtools/templates"

class TemplateGenerator():
	"""
	Generates template for `plugin`, `engine`, `signal`, `generator`.
	"""
	
	@staticmethod
	def ask_questions(for_what: str) -> dict:
		print("----------------------")
		print(for_what.upper())
		print("----------------------")
		module_name = questionary.text("Module name (snake_case): ").ask()
		if module_name is None:
			sys.exit(1)
		if Path(f"src/modusa/{for_what}/{module_name}.py").exists():
			print(f"⚠️ File already exists, choose another name.")
			sys.exit(1)
		
		class_name = questionary.text("Class name (CamelCase): ").ask()
		if class_name is None:
			sys.exit(1)
			
		author_name = questionary.text("Author name: ").ask()
		if author_name is None:
			sys.exit(1)
		
		author_email = questionary.text("Author email: ").ask()
		if author_email is None:
			sys.exit(1)
		
		answers = {"module_name": module_name, "class_name": class_name, "author_name": author_name, "author_email": author_email, "date_created": date.today()}
			
		return answers
	
	@staticmethod
	def load_template_file(for_what: str) -> str:
		template_path = TEMPLATES_DIR / f"{for_what}.py"
		if not template_path.exists():
			print(f"❌ Template not found: {template_path}")
			sys.exit(1)
		
		template_code = template_path.read_text()
		
		return template_code
	
	@staticmethod
	def fill_placeholders(template_code: str, placehoders_dict: dict) -> str:
		template_code = template_code.format(**placehoders_dict)  # Fill placeholders
		return template_code
	
	@staticmethod
	def save_file(content: str, output_path: Path) -> None:
		output_path.parent.mkdir(parents=True, exist_ok=True)
		output_path.write_text(content)
		print(f"✅ Successfully created.\n\n open {output_path.resolve()}")
	
	@staticmethod
	def create_template(for_what: str) -> None:
		
		# Ask basic questions to create the template for `plugin`, `generator`, ...
		answers: dict = TemplateGenerator.ask_questions(for_what)
		
		# Load the correct template file
		template_code: str = TemplateGenerator.load_template_file(for_what)
		
		# Update the dynamic values based on the answers
		template_code: str = TemplateGenerator.fill_placeholders(template_code, answers)
		
		# Save it to a file and put it in the correct folder
		TemplateGenerator.save_file(content=template_code, output_path=ROOT_DIR / f"src/modusa/{for_what}/{answers['module_name']}.py")