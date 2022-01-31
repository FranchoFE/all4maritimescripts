import requests
import json
from datetime import datetime, timedelta
from model.Visit import Visit
from model.Service import Service
from model.Company import Company
from model.ServiceAvailable import ServiceAvailable
import time
import random

# URL = "http://localhost:8092/v1/projects/vuefutbol/databases/(default)/documents/"
URL = "https://firestore.googleapis.com/v1/projects/vuefutbol/databases/(default)/documents/"
TIME_TO_SLEEP = 0.25


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


def create_visits(num_visits, companies, actual_visits_number, ships=(("CEUTA JET", "88888888"), ("ALGECIRAS JET", "1231231"))):
    results = list()
    for i in range(num_visits):
        create_visit = True
        if create_visit:
            company = companies[random.randint(0, len(companies) - 1)].id
            visit_number = "2022" + str(i + actual_visits_number + 1).zfill(5)
            ship = ships[random.randint(0, len(ships) - 1)]
            visit_ = Visit(None, visit_number, ship[0], ship[1], company,
                           datetime.now() + timedelta(hours=6 + i),
                           datetime.now() + timedelta(days=5, hours=i), None, None,
                           "CT_J", "JCIEST", "ESCEU", "MAPTM")
            put_url = URL + "visits"
            result_ = requests.post(put_url, visit_.get_json(None))
            if result_.ok:
                id_ = result_.json()["name"][len("projects/vuefutbol/databases/(default)/documents/visits/"):]
                visit_.id = id_
            else:
                print("Create visit result {}".format(result_))
            results.append(visit_)
            time.sleep(TIME_TO_SLEEP)
    return results


def create_companies(num_companies):
    results = list()
    for i in range(num_companies):
        company_ = Company(None, "name" + str(i), "123123F", "a@a.com")
        put_url = URL + "company"
        result_ = requests.post(put_url, company_.get_json(None))
        if result_.ok:
            id_ = result_.json()["name"][len("projects/vuefutbol/databases/(default)/documents/company/"):]
            company_.id = id_
        else:
            print("Create companies result {}".format(result_))
        results.append(company_)
        time.sleep(TIME_TO_SLEEP)
    return results


def create_services(services_to_create, visits, services_availables):
    results = list()
    for index in range(services_to_create):
        start_time = datetime.now() + timedelta(hours=6 + index)
        end_time = datetime.now() + timedelta(hours=12 + index)
        service_available = services_availables[random.randint(0, len(services_availables) - 1)]
        visit = visits[random.randint(0, len(visits) - 1)]
        service = Service(None, visit.id, service_available.id, "Planned", start_time, end_time, None, None)
        put_url = URL + "services"
        result_ = requests.post(put_url, service.get_json(None))

        if result_.ok:
            id_ = result_.json()["name"][len("projects/vuefutbol/databases/(default)/documents/services/"):]
            service.id = id_
        else:
            print("Create service result {}".format(result_))
        results.append(service)

        time.sleep(TIME_TO_SLEEP)
    return results


def actualize_etas(visit, time_to_set):
    visit.eta = time_to_set
    patch_url = URL + "visits/" + visit.id + "?updateMask.fieldPaths=eta"
    result = requests.patch(patch_url, visit.get_json(("eta", )))
    print("Actualice visit result {}".format(result))
    time.sleep(TIME_TO_SLEEP)


def actualize_service_times(services, service_index, time_to_set_start, time_to_set_end):
    found = False
    if 0 < service_index < len(services) and (time_to_set_start is not None or time_to_set_end is not None):
        found = True
        service = services[service_index]
        patch_url = URL + "services/" + service.id + "?"
        atts_to_get_json = list()
        if time_to_set_start is not None:
            atts_to_get_json.append("real_start_time")
            patch_url += "updateMask.fieldPaths=real_start_time&"
            service.real_start_time = time_to_set_start
        if time_to_set_end is not None:
            atts_to_get_json.append("real_end_time")
            patch_url += "updateMask.fieldPaths=real_end_time"
            service.real_end_time = time_to_set_end

        result = requests.patch(patch_url, service.get_json(atts_to_get_json))
        print("Actualice service result {}".format(result))
        time.sleep(TIME_TO_SLEEP)
    return found


def create_services_available(num_services, companies, types=("BUNKERING", "MARPOL", "REPARACIONES")):
    results = list()
    for i in range(num_services):
        type = types[random.randint(0, len(types)-1)]
        service_available = ServiceAvailable(None, companies[random.randint(0, len(companies)-1)].id, random.randint(10, 100), random.randint(0, 5), type, "EUROS-HORA")
        put_url = URL + "service_available"
        result_ = requests.post(put_url, service_available.get_json(None))

        if result_.ok:
            id_ = result_.json()["name"][len("projects/vuefutbol/databases/(default)/documents/service_available/"):]
            service_available.id = id_
        else:
            print("Create service available result {}".format(result_))
        results.append(service_available)

        time.sleep(TIME_TO_SLEEP)
    return results


def get_time_from_string(time_to_set_str):
    if len(time_to_set_str) > 0 and time_to_set_str != "-1":
        time_to_set = datetime.strptime(time_to_set_str, "%Y-%m-%d %H:%M")
    else:
        time_to_set = datetime.now()
    return time_to_set


if __name__ == '__main__':
    companies_ = get_elements_from_url("company", Company)
    answer = input("\nHay {} compañías disponibles creadas. ¿Cuántas nuevas desea crear?: ".format(len(companies_)))
    if answer.isdigit() and int(answer) > 0:
        companies_.extend(create_companies(int(answer)))
    print("Total de compañías: {}".format(len(companies_)))

    services_availables_ = get_elements_from_url("service_available", ServiceAvailable)
    answer = input("\nHay {} servicios disponibles creados. ¿Cuántos nuevos desea crear?: ".format(len(services_availables_)))
    if answer.isdigit() and int(answer) > 0:
        services_availables_.extend(create_services_available(int(answer), companies_))
    print("Total de tipos de servicio: {}".format(len(services_availables_)))

    visits_ = get_elements_from_url("visits", Visit)
    answer = input("\nHay {} escalas creadas. ¿Cuántas nuevas desea crear?: ".format(len(visits_)))
    if answer.isdigit() and int(answer) > 0:
        visits_.extend(create_visits(int(answer), companies_, len(visits_)))
    print("Total de escalas: {}".format(len(visits_)))

    print("\n")
    actualize_eta = True
    show_visits = True
    while actualize_eta:
        if show_visits:
            print("Escalas: ")
            index = 1
            for visit in visits_:
                visit.print(index)
                index += 1
            show_visits = False
        visit_index = input("¿Quiere actualizar el eta de alguna escala? (Introduzca el índice) ")
        if visit_index.isdigit() and 0 < int(visit_index) <= len(visits_):
            time_to_set_str = input("¿Qué hora quiere establecer? ({}) ".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
            time_to_set = get_time_from_string(time_to_set_str)
            actualize_etas(visits_[int(visit_index)-1], time_to_set)
        else:
            actualize_eta = False
    print("Escala no encontrada")

    services_ = get_elements_from_url("services", Service)
    answer = input("\nHay {} servicios creados. ¿Cuántos nuevos desea crear?: ".format(len(services_)))
    if answer.isdigit() and int(answer) > 0:
        services_.extend(create_services(int(answer), visits_, services_availables_))

    show_services = True
    actualize_service = True
    print("\n")
    while actualize_service:
        if show_services:
            print("Servicios: ")
            index = 1
            for service in services_:
                service.print(visits_, services_availables_, index)
                index += 1
            show_services = False
        service_index = input("¿Quiere actualizar algún servicio? (Introduzca el índice del servicio) ")
        if service_index.isdigit() and 0 < int(service_index) <= len(services_):
            time_to_set_start_str = input("¿Qué hora quiere establecer al inicio del servicio? ({}) (-1 no actualizar) ".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
            time_to_set_end_str = input("¿Qué hora quiere establecer al final del servicio? ({})  (-1 no actualizar) ".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
            time_to_set_start = get_time_from_string(time_to_set_start_str)
            time_to_set_end = get_time_from_string(time_to_set_end_str)
            if time_to_set_start_str == "-1":
                time_to_set_start = None
            if time_to_set_end_str == "-1":
                time_to_set_end = None
            actualize_service = actualize_service_times(services_, int(service_index)-1, time_to_set_start, time_to_set_end)
        else:
            actualize_service = False
