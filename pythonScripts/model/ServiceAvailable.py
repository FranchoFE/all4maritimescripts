from datetime import datetime


class ServiceAvailable:
    def __init__(self, id_, company, price, rating, type_, unit):
        self.id = id_
        self.company = company
        self.price = price
        self.rating = rating
        self.type = type_
        self.unit = unit

    @staticmethod
    def add_field(name, field_type, value):
        if value is None:
            result = "\"" + name + "\": { \"nullValue\": null}, "
        else:
            if isinstance(value, datetime):
                value = value.strftime("%Y-%m-%dT%H:%M:00.000000Z")

            result = "\"" + name + "\": { \"" + field_type + "\": \"" + str(value) + "\"}, "
        return result

    def get_json(self, fields_to_send):
        result = "{ \"fields\": { "
        if fields_to_send is None:
            result += ServiceAvailable.add_field("company_ref", "stringValue", self.company)
            result += ServiceAvailable.add_field("price", "integerValue", self.price)
            result += ServiceAvailable.add_field("rating", "integerValue", self.rating)
            result += ServiceAvailable.add_field("type", "stringValue", self.type)
            result += ServiceAvailable.add_field("unit", "stringValue", self.unit)
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
        company = json_["company_ref"]["stringValue"]
        price = json_["price"]["integerValue"]
        rating = json_["rating"]["integerValue"]
        type_ = json_["type"]["stringValue"]
        unit = json_["unit"]["stringValue"]
        return ServiceAvailable(id_, company, price, rating, type_, unit)

    def print(self):
        print("ServiceAvailable: Company = {}. Type = {}".format(self.company, self.type))

    @classmethod
    def find_service_available(cls, service_available_ref, services_availables):
        return next(filter(lambda service_available: service_available.id == service_available_ref, services_availables), None)
