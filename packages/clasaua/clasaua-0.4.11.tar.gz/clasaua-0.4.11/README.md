# clasaua


## Dependencies

```
python = ">=3.10,<3.13"
odfpy = "^1.4.1"
reportlab = "^4.2.0"
```

## Execute from source

Linux

```
source .venv/bin/activate
python clasaua/launcher.py clasificacion_.ods
```


## Intalación

Instálase e execútase desde terminal

Linux

```
apt-get install python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install clasaua-0.4.7-py3-none-any.whl
clasaua clasificacion_.ods
```

Executar desde o código:
```
poetry run clasauaa ficheiro_coa_clasificacion.ods
```


Windows

Crear cartafol clasaua, na barra de dirección escribir cmd e premer enter, 
aparecerá unha consola na que poder escribir. Poñer o seguinte (despois de cada
liña premer intro):

```
python -m venv venv
venv\Scripts\activate
pip install clasaua-0.4.7-py3-none-any.whl
clasauaa clasificacion_.ods
```

Lanzador desde a contorna gráfica
Crear ficheiro clasaua.bat e dentro do cartafol clasaua onde se instalou, 
poñer dentro do ficheiro creado a liña:
```
venv\Scripts\python.exe venv\Scripts\clasauaa.exe clasificacion_.ods
```

file_path is a ODS file

Columns:
- event_id: is a number from 1
- position: is a number, position relative to gender and category
- license_id: is a number license code identificator
- club_id: is a string of 5 digits, clubs'code
- surname, name: string participant surname, name 
- gender_id: string [M:male|F:female]
- category_id: string [ABSO|MASTER1|MASTER2|MASTER3|MASTER4]

Poetry

add pypi key:
poetry config pypi-token.pypi pypi-BgEI....

poetry update
poetry build
poetry publish


clubs.csv file format, encoding utf8

"CLUBCODE","SHORTNAME","LONG NAME"
"CLUBCODE2","SHORTNAME2","LONG NAME2"

CLUBCODE: 5 digits code, example: P0001
SHORTNAME: short name without spaces, example: CLUBNAME
LONG NAME: full club name, example: C. N. FULL CLUB NAME