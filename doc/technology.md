# Technology

The Wikipedia texts are processed by means of language technology.
The output of the language technology is stored in the [NLP Annotation Format](https://github.com/newsreader/NAF) version 3.1.

We make use of [spaCy](https://spacy.io/) for the following NLP tasks:
* sentence splitting
* tokenization
* lemmatization
* part of speech tagging (using [Universal Dependencies](https://universaldependencies.org/) labels.)
* dependency parsing

The following spaCy language models were used for this release:
* **english**: en_core_web_sm version 2.1.0
* **dutch**: nl_core_news_sm version 2.1.0
* **italian**: it_core_news_sm version 2.1.0

## Entities
Each entity elements originates from a Wikipedia hyperlink as it was there in the
release of Wikipedia from the 20th of July, 2019.
If available, the Wikidata URI of each hyperlink is also added as an external reference to the entity element.

## Coreferences
Most incidents contain both structured and unstructured information about the incident.
There are cases in which a Wikipedia hyperlink in the text is also present in the structured data of the incident.
In these cases, we add a coref element to the coreferences layer.

## Frame detection
The FrameNet frame annotations are added using [open-sesame](https://github.com/swabhs/open-sesame).

## Phrasal verb detection
One of the tag predicated by the dependency parsing is [compound:prt](https://universaldependencies.org/de/dep/compound-prt.html),
which is an edge from a verb head to a verb particle. We exploit this edge to combine the verb head and the verb particle
into one term. We apply this procedure only to Dutch texts.

## The title
The title of each article starts and ends with '++'.

