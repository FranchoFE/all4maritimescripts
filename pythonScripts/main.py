import requests
import json
from datetime import datetime, timedelta
from model.Visit import Visit
import time

URL = "http://localhost:8090/v1/projects/vuefutbol/databases/(default)/documents/visits"


def get_visits_from_url():
    result = list()
    get_from_api = True
    if get_from_api:
        r = requests.get(URL)

        with open('data.txt', 'w') as outfile:
            json.dump(r.json(), outfile)

    read_from_file = True
    if read_from_file:
        with open('data.txt') as json_file:
            data = json.load(json_file)
            if "documents" in data:
                for p in data['documents']:
                    id_ = p["name"][len("projects/vuefutbol/databases/(default)/documents/visits/"):]
                    visit = Visit.from_json(id_, p["fields"])
                    result.append(visit)
                    visit.print()
    return result


def create_visits():
    results = list()
    for i in range(1):
        create_visit = True
        if create_visit:
            visit_ = Visit(None, "20220000" + str(i), "CEUTA JET", "8888888", "FRS", "ffelez@addocean.com",
                           datetime.now() + timedelta(hours=6 + i),
                           datetime.now() + timedelta(days=5, hours=i), None, None)
            results.append(visit_)
            put_url = URL
            result_ = requests.post(put_url, visit_.get_json(None))
            print(result_)
            time.sleep(2)
    return results


def actualize_atas(visits_, visits_to_actualize):
    for visit_ in visits_:
        if visit_.visitNumber in visits_to_actualize:
            visit_.ata = datetime.now()
            patch_url = URL + "/" + visit_.id + "?updateMask.fieldPaths=ata"
            result = requests.patch(patch_url, visit_.get_json(("ata", )))
            print(result)
            print(result.content)
            time.sleep(1)


create_visits()
visits = get_visits_from_url()
actualize_atas(visits, ("202200001", ))


