from datetime import datetime


class Company:
    def __init__(self, id_, name, cif, contact):
        self.id = id_
        self.name = name
        self.cif = cif
        self.contact = contact

    @staticmethod
    def add_field(name, field_type, value):
        if value is None:
            result = "\"" + name + "\": { \"nullValue\": null}, "
        else:
            if isinstance(value, datetime):
                value = value.strftime("%Y-%m-%dT%H:%M:00.000000Z")

            result = "\"" + name + "\": { \"" + field_type + "\": \"" + value + "\"}, "
        return result

    def get_json(self, fields_to_send):
        result = "{ \"fields\": { "
        if fields_to_send is None:
            result += Company.add_field("name", "stringValue", self.name)
            result += Company.add_field("cif", "stringValue", self.cif)
            result += Company.add_field("contact", "stringValue", self.contact)
        result = result[:-2]
        result += " } }"

        print(result)

        return result

    @staticmethod
    def get_timestamp_value(json_, param):
        if "timestampValue" in json_[param]:
            return json_[param]["timestampValue"]
        return ""

    @staticmethod
    def from_json(id_, json_):
        name = json_["name"]["stringValue"]
        cif = json_["cif"]["stringValue"]
        contact = json_["contact"]["stringValue"]
        return Company(id_, name, cif, contact)

    def print(self):
        print("Company: {}. Cif = {}".format(self.name, self.cif))
