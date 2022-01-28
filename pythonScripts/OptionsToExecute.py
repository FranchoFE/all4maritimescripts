import requests
import json
from model.Visit import Visit

SHOW_VISITS = "Ver escalas"
CREATE_VISIT = "Crear escala"

URL = "http://localhost:8091/v1/projects/vuefutbol/databases/(default)/documents/"
TIME_TO_SLEEP = 0.25


class OptionsToExecute:
    def __init__(self):
        pass

    @staticmethod
    def get_elements_from_url(element_name, class_):
        result = list()
        get_from_api = True

        filename = "data-{}.txt".format(element_name)
        if get_from_api:
            r = requests.get(URL + element_name)

            with open(filename, 'w') as outfile:
                json.dump(r.json(), outfile)

        read_from_file = True
        if read_from_file:
            with open(filename) as json_file:
                data = json.load(json_file)
                if "documents" in data:
                    for p in data['documents']:
                        id_ = p["name"][len("projects/vuefutbol/databases/(default)/documents/{}/".format(element_name)):]
                        element = class_.from_json(id_, p["fields"])
                        result.append(element)
                        # element.print()
        return result

    def show_options(self):
        options = list()
        options.extend((SHOW_VISITS, "Ver servicios disponibles", "Ver compañías", "Ver servicios"))
        options.extend((CREATE_VISIT, "Crear servicio disponible", "Crear compañía", "Crear servicio"))
        options.extend(("Modificar ATA de escala", "Modificar servicio"))

        index = 1
        for option in options:
            print("{}) {}\n".format(index, op))
            index += 1
        option_selected_str = input("Seleccione opción: ")
        if option_selected_str.isdigit() and 0 < int(option_selected_str) < len(options):
            option_selected = options[int(option_selected_str)]
            if option_selected == CREATE_VISIT:
                self.create_visit_option()

    def create_visit_option(self):
        visits_ = OptionsToExecute.get_elements_from_url("visits", Visit)
        answer = input("\nHay {} escalas creadas. ¿Cuántas nuevas desea crear?: ".format(len(visits_)))
        if answer.isdigit() and int(answer) > 0:
            visits_.extend(create_visits(int(answer), companies_, len(visits_)))
        print("Total de escalas: {}".format(len(visits_)))
