import os
import lxml.etree as ET

class SageSettingsXML:

    def __init__(self, xmlfilename):
        try:
            self.tree = ET.parse(xmlfilename)
        except IOError:
            return
        sage_fields = self.tree.findall('/sageinput/Field')

        self.sage_fields = []
        for element in sage_fields:
            self.sage_fields.append(Field(element))

    def getNumberOfFields(self):
        return len(self.sage_fields)

    def getItem(self, index):
        return self.sage_fields[index]

    def getFieldWithName(self,name):
        for field in self.sage_fields:
            thisname = field.element.text.lower()
            if thisname == name.lower():
                return field


class Field:

    def __init__(self,element):
        self.element = element
        self.properties = {}
        for key in self.element.keys():
            self.properties[key.lower()] = self.element.get(key)

    def getName(self):
        return self.element.text.lower()

    def getType(self):
        return self.properties['type']
       
    def getLabel(self):
        return self.properties['label']
       
    def getDescription(self):
        return self.properties['description']
       
    def getOrder(self):
        return self.properties['order']
       
    def getUnits(self):
        return self.properties['units']
       
    def getGroup(self):
        return self.properties['group']
