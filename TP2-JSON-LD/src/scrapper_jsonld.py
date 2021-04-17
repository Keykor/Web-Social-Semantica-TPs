import requests
import bs4
import json
import os

def create_data_directory_path(file_name):
    return os.path.abspath(os.path.join(*[os.path.dirname(__file__), os.pardir, "data", file_name]))


if __name__ == "__main__":

    pages_to_scrap = None
    with open(create_data_directory_path('pages_to_scrap.json'), encoding="utf-8") as file:
        pages_to_scrap = json.load(file)

    for page in pages_to_scrap:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
        pageHTML = requests.get(page["url"], headers=headers).text
        soup = bs4.BeautifulSoup(pageHTML, "html.parser")
        data_json = soup.find('script', attrs={"type":"application/ld+json"}).string.replace("\r","").replace("\n","").replace("\t","")
        data = json.loads(data_json)
    
        with open(create_data_directory_path(page["name"] + ".json"),"w",encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)