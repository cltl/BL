# Release notes of data release v1.0

This document contains the information about the data release v1.0.

Directory structure:
* [CC0.md](CC0 1.0 Universal): CC0 1.0 Universal License
* [Apache_2.0.md](Apache_2.0.md): Apache 2.0 License
* [CC-BY-SA-3.0.md](CC-BY-SA-3.0.md): CC-BY-SA License
* [lexical_resources](lexical_resources): 
    * [lexical resources README](lexical_resources/README.md): information about the lexical information, mainly used in the [annotation tool](https://github.com/cltl/frame-annotation-tool)
    * [typical_frames](lexical_resources/typical_frames.json): the 10 typical frames for each event types according to a contrastive analysis (see in the paper Section 6.3)
* [structured](structured)
    * [inc2doc_index.json](structured/inc2doc_index.json): contains a mapping from an Incident ID (e.g., Q51336711) to the ReferenceTexts that refer to it (as found in the folder **unstructured**).
    * [inc2str_index.json](structured/inc2str_index.json): contains a mapping from an Incident ID to the structured data of the incident as represented using [SEM](https://semanticweb.cs.vu.nl/2009/11/sem/) (see the paper Section 4).
    * [proj2inc_index](structured/proj2inc_index.json): contains a mapping from a project, e.g., v1, to the Incidents that belong to it.
    * [type2inc_index](structured/type2inc_index.json): contains a mapping from an event type to the Incidents that belong to it.
    * [structured_and_unstructured](structured/structured_and_unstructured.json): one JSON containing both the structured and unstructured data.
* [rdf](rdf)
    * [v1.ttl](rdf/v1.ttl) [SEM](https://semanticweb.cs.vu.nl/2009/11/sem/) representation of the structured data
* [unstructured](unstructured) (see [technology](technology.md) for the language technology applied.)
    * [en](en): contains English [NAF version 3.1](https://github.com/newsreader/NAF) files
    * [nl](nl): contains Dutch [NAF version 3.1](https://github.com/newsreader/NAF) files
    * [it](it): contains Italian [NAF version 3.1](https://github.com/newsreader/NAF) files
* [statistics](statistics)
    * [Relation EventType to Incident](statistics/event_type_to_num_of_incidents.csv): for each event type, the number of incidents is reported.
    * [Descriptive statistics EventType to Incident](statistics/event_type_to_inc_stats.csv): descriptive statistics of mapping from an event type to the number of incidents.
    * [Properties of Incidents](statistics/incidents.csv): for each incidents, information is shown about the structured data and the number of reference texts per language.
    * [Descriptive statistics Incidents](statistics/incident_stats.csv): descriptive statistics of the structured and unstructured data of the Incidents.
    * [Properties of ReferenceTexts](statistics/reference_texts.csv): lexical information about each reference text
    * [Descriptive statistics ReferenceTexts](statistics/reference_text_stats.csv): descriptive statistics of the lexical information in the reference texts.
    * [Provenance of frame annotations](statistics/sentences.csv): overview of the number of gold, silver and bronze sentences per reference text. A sentence is gold if all annotations are manually checked, silver is when a subset is manually checked and a sentence is bronze if all frame annotations have been done by a system.
    * [Descriptive statistics frame annotations](statistics/sentence_stats): descriptive statistics of gold, silver, and bronze sentences in the reference texts.