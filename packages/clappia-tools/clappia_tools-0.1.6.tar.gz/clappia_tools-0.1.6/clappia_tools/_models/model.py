import os
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Field:
    """Field model for creating an app"""
    """
    fieldType: str
    label: str
    options: Optional[List[str]] = None
    """

    fieldType: str
    label: str
    options: Optional[List[str]] = None
    def to_dict(self) -> dict:
        result = {
            "fieldType": self.fieldType,
            "label": self.label,
        }
        if self.options is not None:
            result["options"] = self.options
        return result

@dataclass
class Section:
    """Section model for creating an app"""
    """
    sectionName: str
    fields: List[Field]
    """
    
    sectionName: str
    fields: List[Field]
    def to_dict(self) -> dict:
        return {
            "sectionName": self.sectionName,
            "fields": [field.to_dict() for field in self.fields]
        }