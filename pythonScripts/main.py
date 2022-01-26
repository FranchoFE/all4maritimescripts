import requests
import json
from datetime import datetime, timedelta
from model.Visit import Visit
from model.Service import Service
from model.Company import Company
from model.ServiceAvailable import ServiceAvailable
import time
import random

URL = "http://localhost:8090/v1/projects/vuefutbol/databases/(default)/documents/"


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
                    element.print()
    return result


def create_visits(num_visits, companies):
    results = list()
    for i in range(num_visits):
        create_visit = True
        if create_visit:
            company = companies[random.randint(0, len(companies) - 1)].id
            visit_ = Visit(None, "20220000" + str(i), "CEUTA JET", "8888888", company,
                           datetime.now() + timedelta(hours=6 + i),
                           datetime.now() + timedelta(days=5, hours=i), None, None,
                           "CT_J", "JCIEST", "ESCEU", "MAPTM")
            put_url = URL + "visits"
            result_ = requests.post(put_url, visit_.get_json(None))
            if result_.ok:
                id_ = result_.json()["name"][len("projects/vuefutbol/databases/(default)/documents/visits/"):]
                visit_.id = id_
            results.append(visit_)
            print("Create visit result {}".format(result_))
            time.sleep(2)
    return results


def create_companies(num_companies):
    results = list()
    for i in range(num_companies):
        company_ = Company(None, "name" + str(i), "123123F", "a@a.com")
        put_url = URL + "company"
        result_ = requests.post(put_url, company_.get_json(None))
        print("Create companies result {}".format(result_))
        if result_.ok:
            id_ = result_.json()["name"][len("projects/vuefutbol/databases/(default)/documents/company/"):]
            company_.id = id_
        results.append(company_)
        time.sleep(2)
    return results


def find_visit(visits_, visit_number):
    return next(filter(lambda visit: visit.visitNumber == visit_number, visits_), None)


def create_services(visits_, services_to_create):
    results = list()
    index = 0
    for service_to_create in services_to_create:
        index += 1
        start_time = datetime.now() + timedelta(hours=6 + index)
        end_time = datetime.now() + timedelta(hours=12 + index)
        visit = find_visit(visits_, service_to_create)
        company = "CEPSA"
        if index % 2 == 0:
            company = "VOPAK"
        service = Service(None, visit.id, company, "bunkering", start_time, end_time)
        results.append(service)
        put_url = URL + "services"
        result_ = requests.post(put_url, service.get_json(None))
        print("Create service result {}".format(result_))
        time.sleep(2)
    return results


def actualize_atas(visits_, visits_to_actualize):
    for visit_ in visits_:
        if visit_.visitNumber in visits_to_actualize:
            visit_.ata = datetime.now()
            patch_url = URL + "visits/" + visit_.id + "?updateMask.fieldPaths=ata"
            result = requests.patch(patch_url, visit_.get_json(("ata", )))
            print("Actualice visit result {}".format(result))
            time.sleep(1)


def create_services_available(num_services, companies):
    results = list()
    for i in range(num_services):
        service_available = ServiceAvailable(None, companies[random.randint(0, len(companies)-1)].id, 1, 2, "type", "unit")
        results.append(service_available)
        put_url = URL + "service_available"
        result_ = requests.post(put_url, service_available.get_json(None))
        print("Create service available result {}".format(result_))
        time.sleep(2)
    return results


companies = create_companies(5)
create_services_available(5, companies)
visits_ = create_visits(5, companies)
actualize_atas(visits_, ("202200001", ))
# create_services(visits_, ("202200002", "202200002", "202200002", "202200002", "202200003"))

