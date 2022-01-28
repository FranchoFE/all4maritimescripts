from datetime import datetime
from model.Visit import Visit
from model.ServiceAvailable import ServiceAvailable


class Service:
    def __init__(self, id_, visit, service_available_ref, state, estimated_start_time, estimated_end_time, real_start_time, real_end_time):
        self.id = id_
        self.service_available_ref = service_available_ref
        self.visit = visit
        self.state = state
        self.estimated_start_time = estimated_start_time
        self.estimated_end_time = estimated_end_time
        self.real_start_time = real_start_time
        self.real_end_time = real_end_time

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
            result += Service.add_field("service_available_ref", "stringValue", self.service_available_ref)
            result += Service.add_field("state", "stringValue", self.state)
            result += Service.add_field("visit_ref", "stringValue", self.visit)
            result += Service.add_field("estimated_start_time", "timestampValue", self.estimated_start_time)
            result += Service.add_field("estimated_end_time", "timestampValue", self.estimated_end_time)
            result += Service.add_field("real_start_time", "timestampValue", self.real_start_time)
            result += Service.add_field("real_end_time", "timestampValue", self.real_end_time)
        else:
            if "real_start_time" in fields_to_send:
                result += Service.add_field("real_start_time", "timestampValue", self.real_start_time)
            if "real_end_time" in fields_to_send:
                result += Service.add_field("real_end_time", "timestampValue", self.real_end_time)
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
        service_available_ref = json_["service_available_ref"]["stringValue"]
        visit = json_["visit_ref"]["stringValue"]
        state = json_["state"]["stringValue"]
        estimated_start_time = Service.get_timestamp_value(json_, "estimated_start_time")
        estimated_end_time = Service.get_timestamp_value(json_, "estimated_end_time")
        real_start_time = Service.get_timestamp_value(json_, "real_start_time")
        real_end_time = Service.get_timestamp_value(json_, "real_end_time")
        return Service(id_, visit, service_available_ref, state, estimated_start_time, estimated_end_time, real_start_time, real_end_time)

    def print(self, visits=(), services_availables=(), index=None):
        visit = Visit.find_visit(self.visit, visits)
        if visit is None:
            visit_to_show = self.visit
        else:
            visit_to_show = visit.visitNumber
        service = ServiceAvailable.find_service_available(self.service_available_ref, services_availables)
        if service is None:
            service_to_show = self.service_available_ref
        else:
            service_to_show = service.type
        index_to_show = ""
        if index is not None:
            index_to_show = "{}) ".format(index)
        print("{}{} - {} - Visit = {}. Start time = {}. End time = {}".format(
            index_to_show, self.state, service_to_show, visit_to_show, self.real_start_time, self.real_end_time))
