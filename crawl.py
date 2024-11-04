import os
from aprec.datasets.download_file import download_file
from aprec.datasets.movielens1m import get_movies_catalog

from tqdm import tqdm
import json
import requests

from aprec.utils.os_utils import get_dir

DBPEDIA_MAPPING_FILE = "dbpedia_mapping.tsv"
DBPEDIA_ABSTRACTS_FILE = "dbpedia_abstracts.json"
TOTAL_DBPEDIA_MAPPINGS = 3300
MOVIELENS_DIR = "data/movielens1m"
DBPEDIA_MAPPING_URL = "https://raw.githubusercontent.com/asash/LODrecsys-datasets/refs/heads/master/Movielens1M/MappingMovielens2DBpedia-1.2.tsv"



class ML1MDbpediaAbstracts(object):
    def __init__(self):
        self.catalog = get_movies_catalog()

    def get_ml1m_movie_abstracts(self):
        dbpedia_file = download_file(DBPEDIA_MAPPING_URL, DBPEDIA_MAPPING_FILE, MOVIELENS_DIR)
        result = {}
        full_filename = os.path.join(get_dir(), MOVIELENS_DIR, DBPEDIA_ABSTRACTS_FILE)
        for line in tqdm(open(dbpedia_file), total=TOTAL_DBPEDIA_MAPPINGS):
            id, movielens_title, dbpedia_resource = line.strip().split("\t")
            dbpedia_url = dbpedia_resource.replace("/resource/", "/data/") + ".json"
            default_abstract = self.get_default_abstract(id)

            try:
                response = json.loads(requests.get(dbpedia_url).text)[dbpedia_resource]
                print(id, movielens_title)
                abstract = response.get("http://dbpedia.org/ontology/abstract", default_abstract)
            except:
                abstract = default_abstract
                print("Exception! returning default abstract..")

            english_abstract = next((item['value'] for item in abstract if item['lang'] == 'en'), "Abstract not found.")
            result[id] = english_abstract

        with open(full_filename, "w") as out:
            json.dump(result, out, indent=4)
        return full_filename

    def get_default_abstract(self, id):
        item =self.catalog.get_item(id)
        result = [{"value": f"Movie: {item.title}, Genres: {item.tags}", "lang": 'en'}]
        return result

if __name__ == "__main__":
    ml1m_dbpedia_abstracts = ML1MDbpediaAbstracts()
    result = ml1m_dbpedia_abstracts.get_ml1m_movie_abstracts()
    print(result)
