# Incorporating MWEP

We use the [MWEP](https://github.com/cltl/multilingual-wiki-event-pipeline) repository
to extract Incidents and ReferenceTexts from Wikidata. The resulting data can then be incorporated into the 
EventTypeCollection as defined in **wd_classes.py**.

This can be achieved by calling the bash script called **mwep_integration.sh** as found in the folder **scripts**.
This script calls **mwep_integration.py** which you can call to obtain more information on how to use it.

Each run of **mwep_integration.sh** loads an EventTypeCollection, updates it with MWEP information and
overwrites the EventTypeCollection that was previously stored on disk.