from datetime import datetime


class Visit:
    def __init__(self, id_, visit_number, vessel_name, imo, company, eta, etd, ata, atd, call_sign, code_zone_operation, port_previous, port_next):
        self.id = id_
        self.visitNumber = visit_number
        self.vesselName = vessel_name
        self.imo = imo
        self.company = company
        self.eta = eta
        self.etd = etd
        self.ata = ata
        self.atd = atd
        self.call_sign = call_sign
        self.code_zone_operation = code_zone_operation
        self.port_previous = port_previous
        self.port_next = port_next

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
            result += Visit.add_field("visit_number", "stringValue", self.visitNumber)
            result += Visit.add_field("imo", "stringValue", self.imo)
            result += Visit.add_field("vessel_name", "stringValue", self.vesselName)
            result += Visit.add_field("company_ref", "stringValue", self.company)
            result += Visit.add_field("call_sign", "stringValue", self.call_sign)
            result += Visit.add_field("code_zone_operation", "stringValue", self.code_zone_operation)
            result += Visit.add_field("port_previous", "stringValue", self.port_previous)
            result += Visit.add_field("port_next", "stringValue", self.port_next)
            result += Visit.add_field("eta", "timestampValue", self.eta)
            result += Visit.add_field("etd", "timestampValue", self.etd)
            result += Visit.add_field("ata", "timestampValue", self.ata)
            result += Visit.add_field("atd", "timestampValue", self.atd)
        elif "ata" in fields_to_send:
            result += Visit.add_field("ata", "timestampValue", self.ata)
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
        visitNumber = json_["visit_number"]["stringValue"]
        vessel_name = json_["vessel_name"]["stringValue"]
        company = json_["company_ref"]["stringValue"]
        imo = json_["imo"]["stringValue"]
        call_sign = json_["call_sign"]["stringValue"]
        code_zone_operation = json_["code_zone_operation"]["stringValue"]
        port_previous = json_["port_previous"]["stringValue"]
        port_next = json_["port_next"]["stringValue"]
        eta = Visit.get_timestamp_value(json_, "eta")
        etd = Visit.get_timestamp_value(json_, "etd")
        ata = Visit.get_timestamp_value(json_, "ata")
        atd = Visit.get_timestamp_value(json_, "atd")
        return Visit(id_, visitNumber, vessel_name, imo, company, eta, etd, ata, atd, call_sign, code_zone_operation, port_previous, port_next)

    def print(self, index=None):
        index_to_show = ""
        if index is not None:
            index_to_show = "{}) ".format(index)
        print("{}Visit: {}. Vessel = {}".format(index_to_show, self.visitNumber, self.vesselName))

    @classmethod
    def find_visit(cls, visit_id, visits):
        return next(filter(lambda visit: visit.id == visit_id, visits), None)
