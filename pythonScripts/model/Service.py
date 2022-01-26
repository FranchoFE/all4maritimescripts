from datetime import datetime


class Service:
    def __init__(self, id_, visit, company, type_, start_time, end_time):
        self.id = id_
        self.company = company
        self.visit = visit
        self.type = type_
        self.start_time = start_time
        self.end_time = end_time

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
            result += Service.add_field("company", "stringValue", self.company)
            result += Service.add_field("type", "stringValue", self.type)
            result += Service.add_field("visit", "stringValue", self.visit)
            result += Service.add_field("start_time", "timestampValue", self.start_time)
            result += Service.add_field("end_time", "timestampValue", self.end_time)
        elif "start_time" in fields_to_send:
            result += Service.add_field("start_time", "timestampValue", self.start_time)
        elif "end_time" in fields_to_send:
            result += Service.add_field("end_time", "timestampValue", self.end_time)
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
        company = json_["company"]["stringValue"]
        visit = json_["visit"]["stringValue"]
        type_ = json_["type"]["stringValue"]
        start_time = Service.get_timestamp_value(json_, "start_time")
        end_time = Service.get_timestamp_value(json_, "end_time")
        return Service(id_, visit, company, type_, start_time, end_time)

    def print(self):
        print("Service: {}. Company = {}. Visit = {}".format(self.type, self.company, self.visit))
