import scrapper_jsonld
import scrapper_cinepolis
import cinemalaplata_to_turtle
import combine_graphs

if __name__ == "__main__":
    print("Comienza extracción de páginas con JSON-LD")
    scrapper_jsonld.main()
    print("Finaliza extracción de páginas con JSON-LD")
    print("Resultado en archivo 'individuals.ttl'")
    print("Comienza extracción de Cinepolis")
    scrapper_cinepolis.main()
    print("Finaliza extracción de Cinepolis")
    print("Resultado en archivo 'individualsCinepolis.ttl'")
    print("Comienza transformación de resultados anteriores de Cinema La Plata")
    cinemalaplata_to_turtle.main()
    print("Finaliza transformación de resultados anteriores de Cinema La Plata")
    print("Resultado en archivo 'individualsCinemalaplata.ttl'")
    print("Comienza combinación del vocabulario con individuals")
    combine_graphs.main()
    print("Finaliza combinación del vocabulario con individuals")
    print("Resultado final en archivo 'allCombinated.ttl'")