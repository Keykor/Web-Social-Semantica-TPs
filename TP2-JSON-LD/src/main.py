import scrapper_jsonld
import merge_data
import normalize

if __name__ == "__main__":
    print('Scrapping iniciado')
    scrapper_jsonld.main()
    print('Scrapping finalizado')
    print('Normalizacion iniciada')
    normalize.main()
    print('Normalizacion finalizada')
    print('Merge iniciado')
    merge_data.main()
    print('Merge finalizado')
