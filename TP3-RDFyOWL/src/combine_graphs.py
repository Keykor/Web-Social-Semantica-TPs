from rdflib import Graph
import os

def create_data_directory_path(file_name):
    return os.path.abspath(os.path.join(*[os.path.dirname(__file__), os.pardir, "data", file_name]))

def main():
    filenames = ['individuals.ttl', 'individualsCinemalaplata.ttl', 'individualsCinepolis.ttl']
    with open(create_data_directory_path('all.ttl'), 'w', encoding="utf-8") as outfile:
        for fname in filenames:
            with open(create_data_directory_path(fname), encoding="utf-8") as infile:
                for line in infile.readlines()[4:]:
                    outfile.write(line)

if __name__ == "__main__":
    main()