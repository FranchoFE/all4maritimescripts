from datetime import datetime


class Visit:
    def __init__(self, id_, visit_number, vessel_name, imo, company, receiver, eta, etd, ata, atd):
        self.id = id_
        self.visitNumber = visit_number
        self.vesselName = vessel_name
        self.imo = imo
        self.company = company
        self.eta = eta
        self.etd = etd
        self.ata = ata
        self.atd = atd
        self.receiver = receiver

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
            result += Visit.add_field("visitNumber", "stringValue", self.visitNumber)
            result += Visit.add_field("imo", "stringValue", self.imo)
            result += Visit.add_field("vessel_name", "stringValue", self.vesselName)
            result += Visit.add_field("company", "stringValue", self.company)
            result += Visit.add_field("receiver", "stringValue", self.receiver)
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
        visitNumber = json_["visitNumber"]["stringValue"]
        vessel_name = json_["vessel_name"]["stringValue"]
        company = json_["company"]["stringValue"]
        imo = json_["imo"]["stringValue"]
        receiver = json_["receiver"]["stringValue"]
        eta = Visit.get_timestamp_value(json_, "eta")
        etd = Visit.get_timestamp_value(json_, "etd")
        ata = Visit.get_timestamp_value(json_, "ata")
        atd = Visit.get_timestamp_value(json_, "atd")
        return Visit(id_, visitNumber, vessel_name, imo, company, receiver, eta, etd, ata, atd)

    def print(self):
        print("Visit: {}. Vessel = {}".format(self.visitNumber, self.vesselName))
