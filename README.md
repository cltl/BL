# Basic Level

The goal of this repository is to perform experiments to gain insights
into the Basic Level (Event). The most used resource is [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page).

### Prerequisites

Python 3.6 was used to create this project. It might work with older versions of Python.

### Usage
This repository has several purposes:
1. represent Wikidata in Python classes (see [Wikidata Representation](documentation/wikidata_representation.md) )
2. Incorporating output from [MWEP](https://github.com/cltl/multilingual-wiki-event-pipeline) into the Wikidata representation. (see [Incorporating MWEP into Wikidata representation](documentation/incorporating_MWEP.md) )
3. Basic Level Detection (see [Basic Level Detection](documentation/basic_level_detection.md))

### Python modules
A number of external modules need to be installed, which are listed in **requirements.txt**.
Depending on how you installed Python, you can probably install the requirements using one of following commands:
```bash
pip install -r requirements.txt
```

## Action points
* vizualize graph
* labels in n languages, notably Dutch and Italian
* facilitate to move higher than event node in representing Wikidata
* possibility of retagging incidents with other event type(s)

## Authors
* **Marten Postma** (m.c.postma@vu.nl)

## License
This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details
