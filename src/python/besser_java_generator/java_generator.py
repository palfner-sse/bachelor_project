import os

from jinja2 import Environment, FileSystemLoader
from besser.BUML.metamodel.structural import DomainModel
from besser.generators import GeneratorInterface

"""
Generates Java source files for each class and enumeration in a BESSER B-UML domain model.

Extends GeneratorInterface and uses two Jinja2 templates:
    - java_template.py.j2      : produces one .java class file per Class, sorted by
                                  inheritance order so parent classes are always generated
                                  before their children.
    - java_enum_template.py.j2 : produces one .java enum file per Enumeration.

Differences from the original BESSER JavaGenerator:
    - Generates Java enum files for all Enumeration types in the model.
    - Respects is_navigable on association ends — only generates fields for navigable ends.
    - Generates method stubs from class_obj.methods defined in the model.
    - Fixes the leading comma bug in the overloaded constructor when a class has no attributes.

Args:
    model       : DomainModel   - The B-UML domain model containing the types to generate.
    output_dir  : str | None    - Directory where .java files are written.
                                  Also used as the Java package name unless it contains
                                  'tmp' or 'AppData', in which case no package is declared.
"""
class JavaGenerator(GeneratorInterface):

    def __init__(self, model: DomainModel, output_dir: str = None):
        super().__init__(model, output_dir)

    """
    Generates one .java file per Enumeration (via java_enum_template.py.j2) and one per
    Class (via java_template.py.j2). A shared processed_associations list is passed to
    the class template across all iterations to prevent duplicate association fields.
    """
    def generate(self):
        templates_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "..", "..", "jinja2")
        env = Environment(loader=FileSystemLoader(
            templates_path), trim_blocks=True, lstrip_blocks=True, extensions=['jinja2.ext.do'])

        if self.output_dir is not None:
            if 'tmp' in self.output_dir or 'AppData' in self.output_dir:
                package_name = None
            else:
                package_name = self.output_dir
        else:
            package_name = None

        for enum_obj in self.model.get_enumerations():
            file_path = self.build_generation_path(file_name=enum_obj.name + ".java")
            template = env.get_template('java_enum_template.py.j2')
            with open(file_path, mode="w") as f:
                f.write(template.render(enum_obj=enum_obj, package_name=package_name))
                print("Code generated in the location: " + file_path)

        processed_associations = []
        for class_obj in self.model.classes_sorted_by_inheritance():
            file_path = self.build_generation_path(file_name=class_obj.name + ".java")
            template = env.get_template('java_template.py.j2')
            with open(file_path, mode="w") as f:
                generated_code = template.render(class_obj=class_obj,
                                                 processed_associations=processed_associations,
                                                 package_name=package_name)
                f.write(generated_code)
                print("Code generated in the location: " + file_path)
