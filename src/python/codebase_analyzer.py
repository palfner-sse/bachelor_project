"""
Analyzer for counting changeable elements in BESSER B-UML models.
"""

from besser.BUML.metamodel.structural import DomainModel, Class, Enumeration

"""
Count all changeable elements per class/enum and as totals.

Args:
    model: A BESSER DomainModel instance

Returns:
    Dictionary with per-class/enum breakdowns and overall totals
"""
def analyze_model(model: DomainModel) -> dict:
    result = {}

    # Totals accumulators
    total_attributes = 0
    total_methods = 0
    total_associations = 0
    total_inheritance = 0
    total_enum_values = 0

    # Count per class
    classes = [e for e in model.elements if isinstance(e, Class)]
    total_classes = len(classes)
    for cls in classes:
        class_data = {
            "class_declaration": 1,
            "attributes": len(cls.attributes),
            "methods": len(cls.methods),
            "associations": 0,
            "inheritance": 0
        }

        total_attributes += class_data["attributes"]
        total_methods += class_data["methods"]

        if hasattr(cls, 'generalizations') and cls.generalizations:
            class_data["inheritance"] = len(cls.generalizations)
            total_inheritance += class_data["inheritance"]

        class_data["total"] = (class_data["class_declaration"] + class_data["attributes"] +
                               class_data["methods"] + class_data["associations"] +
                               class_data["inheritance"])
        result[cls.name] = class_data

    # Count navigable associations per class
    if hasattr(model, 'associations'):
        for assoc in model.associations:
            if hasattr(assoc, 'ends'):
                for end in assoc.ends:
                    if hasattr(end, 'is_navigable') and end.is_navigable:
                        class_obj = end.type
                        if class_obj and hasattr(class_obj, 'name'):
                            if class_obj.name not in result:
                                result[class_obj.name] = {
                                    "class_declaration": 1,
                                    "attributes": 0,
                                    "methods": 0,
                                    "associations": 0,
                                    "inheritance": 0
                                }
                            result[class_obj.name]["associations"] += 1
                            total_associations += 1
                            # Recalculate total without including the old total value
                            class_result = result[class_obj.name]
                            class_result["total"] = (class_result.get("class_declaration", 0) + class_result["attributes"] +
                                                     class_result["methods"] + class_result["associations"] +
                                                     class_result["inheritance"])

    # Count per enumeration
    enums = [e for e in model.elements if isinstance(e, Enumeration)]
    total_enumerations = len(enums)
    for enum in enums:
        enum_value_count = len(enum.literals) if hasattr(enum, 'literals') else 0
        result[enum.name] = {
            "enum_declaration": 1,
            "enum_values": enum_value_count,
            "total": 1 + enum_value_count
        }
        total_enum_values += enum_value_count

    # Add totals
    result["total"] = {
        "classes": total_classes,
        "attributes": total_attributes,
        "methods": total_methods,
        "associations": total_associations,
        "inheritance_relationships": total_inheritance,
        "enumerations": total_enumerations,
        "enum_values": total_enum_values,
        "total": (total_classes + total_attributes + total_methods + total_associations +
                  total_inheritance + total_enumerations + total_enum_values)
    }

    return result
