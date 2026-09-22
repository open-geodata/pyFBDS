# Histórico

Em novembro de 2022 surgiu a necessidade/curiosidade de melhor compreender os dados de hidrologia e uso do solo disponibilizados pela [Fundação Brasileira para o Desenvolvimento Sustentável (FBDS)](https://www.fbds.org.br). Os dados são utilizados em projetos de pesquisa (Biota-Síntese e outros) e são disponibilizados em um [**repositório público de mapas e _shapefiles_ para _download_**](https://geo.fbds.org.br/).

Para obter os dados desenvolvi _scripts_ para fazer o _download_ dos _layers_ do estado de São Paulo. As rotinas podem ser usadas para outros estados. O resultado formou a criação de 7 _layers_ em formato _geopackage_:

| id  | _Layer_              | Subpasta    | Tamanho |
| :-- | :------------------- | :---------- | ------: |
| 1   | app.gpkg             | APP         |  994 MB |
| 2   | app_uso.gpkg         | APP         | 2,07 GB |
| 3   | hidro_simples.gpkg   | HIDROGRAFIA |  673 MB |
| 4   | hidro_duplas.gpkg    | HIDROGRAFIA | 93,8 MB |
| 5   | hidro_nascentes.gpkg | HIDROGRAFIA | 60,0 MB |
| 6   | hidro_massa.gpkg     | HIDROGRAFIA |  124 MB |
| 7   | uso.gpkg             | USO         | 3,89 GB |
|     | Total                |             | 7,87 GB |
