# sws-mind

## Descrizione del progetto

Il progetto consiste nella realizzazione di una infrastruttura hardware e di contenuto software. Lo scopo sarà quello di consolidare il knowhow tecnico ingegneristico e per dare la possibilità ai professionisti di sws di utilizzarlo in modo confortevole per velocità ed aspetto.

L'infrastruttura hardware sarà un server in grado di processare richieste di vario tipo da parte di un client. Quest'ultimo sarà totalmente agnostico delle modalità di esecuzione del server e potrà unicamente effettuare chiamate ed attendere risposte su uno dei protocolli progettati per tale scopo. Le risposte potranno essere flussi di dati o interi file.

Tale suddivisione risulta necessaria per varie ragioni.

1. **indipendenza di sviluppo:** significa che una volta stabilito il protocollo di comunicazione si potrà sviluppare in contemporanea sia lato server che lato client. Ad esempio durante l'aggiunta di codice nel server necessario all'esecuzione di un preciso task, il client potrà contemporaneamente essere preparato per ricevere i risultati in forma visuale.
1. **separazione di competenze:** poichè spesso per il contenuto del codice sorgente sarà necessario il lavoro di ingegneri esperti nelle varie materie (gallerie, ponti, F.E.M.), nel lavoro sul client si potranno utilizzare anche solo esperti informatici.
1. **gestione multiutente** da varie parti del mondo potrebbe essere necessario effettuare richieste al server anche contemporaneamente. In tal caso sarà necessario il possesso del software all'interno dei vari client e tale software (ad esempio su tablet o pc) invierà richieste allo stesso server.
1. **gestione della qualità** con la scoperta di errori o bugs all'interno del codice, ci si potrà concentrare sulla loro risoluzione senza necessità di aggiornare il software sul client.
1. **closed source per clienti** sarà possibile vendere servizi o microservizi ad imprese o amministrazioni pubbliche senza che queste possano conoscere il contenuto tecnico ingegneristico e gli algoritmi necessari alla realizzazione del prodotto-servizio.
1. **gestione delle autorizzazioni** sarà possibile ad esempio fornire l'autorizzazione ad un utente dell'organizzazione ad effettuare dei task per un determinato periodo di tempo. Potrà inoltre essere venduto un prodotto-servizio all'esterno con licenza a tempo.

## Fasi di sviluppo

1. **individuazione degli strumenti informatici hard e soft client e server**
   1. Selezionare l'hardware del server e del client
   1. Decidere il protocollo di comunicazione client/server
1. **progettazione di alcuni piccoli prodotto-servizio o di qualche microservizio**
1. **realizzazione dell'hardware e software necessario al server**
   1. Realizzazione del software
   1. Realizzazione dell'hardware
1. **realizzazione del microservizio sul server**
   1. implementazione del microervizio
   1. collegare il microservizio al protocollo di comunicazione scelto
1. **realizzazione del software su un tipo di client e testare la comunicazione col server**

## Docker container

You can run the REST API inside a docker container with the following command:

```shell
docker run -d Dockerfile --name pycivile -p 8000:8000 -e UVICORN_BIND=0.0.0.0
```

> **NOTE**: the environment variable UVICORN_BIND tells the web server on which address to listen to.
> 0.0.0.0 allows you to reach the API from everywhere, but can be a security risk!

Or, if you don't want to clone the repository:

```shell
docker build -t pycivile https://gitlab.com/luigi_paone/pycivile.git
docker run -d pycivile --name pycivile -p 8000:8000 -e UVICORN_BIND=0.0.0.0
```

Or, if you're a docker-compose guy, you can run the [docker-compose.yml](docker-compose.yml) file with:

```shell
docker-compose up
```

This will also create the database (mongodb) and Code_Aster containers.

### Environment variables

| Name                   | Description                                  | Default                            |
| ---------------------- | -------------------------------------------- | ---------------------------------- |
| `WORKING_DATA_PATH`    | Path for data storage                        | `/app/working-data`                |
| `XLS_SHEETS_DATA_PATH` | Folder with structural calculation workbooks | `/app/res/excel-structural-sheets` |
| `DB_HOST`              | Database hostname                            | `localhost`                        |
| `DB_PORT`              | Database Port                                | `27013`                            |
| `DB_USERNAME`          | Database username                            | empty (no user)                    |
| `DB_PASSWORD`          | Database password                            | empty (no password)                |

## Development

- Install [poetry](https://python-poetry.org/docs/#installation) and [task](https://taskfile.dev/installation/)
- run `task init` do initialize the python environment and install the pre-commit hooks
- before committing code changes, you can run `task` to perform automated checks. You can also run them separately:
  - `task lint` fixes and checks the code and documentation
  - `task mypy` performs type checking
  - `task test` runs the tests with `pytest`
  - `task security` scans the dependencies for known vulnerabilities

> **NOTE**: the `lint` task is executed automatically when you commit the changes to ensure that only good quality code is added to the repository.

## Launch tests with unittest

### Local development

You need to use

```shell
export BASE_PATH_RES=<resources path> && export WORKING_DATA_PATH=<working data>
source goTests
```

where *resources path* typically is sibling of pycivil module and
*working data* were backend can write singles job.

Normally on my pc:

```shell
export BASE_PATH_RES=./res && export WORKING_DATA_PATH=$HOME/Documents/dev/run/pycivile/working-data
```

### Container development

Go into container shell with:

```shell
docker compose exec -ti pycivile /bin/bash
```

and then

```shell
/bin/bash goTests
```

#### Remove all volumes

This remove all volumes and data. Next relaunch the volumes will be build

```shell
docker-compose down -v
```
