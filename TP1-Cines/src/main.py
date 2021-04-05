import scrapper_cinemalaplata
import scrapper_cinepolis
import merge_data

if __name__ == "__main__":
    scrapper_cinemalaplata.main()
    scrapper_cinepolis.main()
    merge_data.main()