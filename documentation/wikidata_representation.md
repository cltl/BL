# Wikidata representation

There is one Bash script that is used to represent Wikidata in Python classes.
([represent_wd.sh](../scripts/represent_wd.sh)).


## Wikidata queries
The first goal of this Bash script is to run SPARQL queries on Wikidata.
The queries are located in the Python module **wd_utils.py**, in the variable QUERIES.

| Query        | Explanation           | 
| :-------------: |:-------------:| 
| **subclass_of**     | extract all [**subclass of**](https://www.wikidata.org/wiki/Property:P279) relationships | 
| **instance_of**      | extract all [**instance of**](https://www.wikidata.org/wiki/Property:P31) relations for those Wikidata items that are descendants of the [event node](https://www.wikidata.org/wiki/Q1656682). Please note that this excludes [**murder**](https://www.wikidata.org/wiki/Q132821).      |  
| **inc_to_props** | for each found incident from the **instance_of** query, we query for all properties, i.e., with the namespace [wdt:](https://www.wikidata.org/wiki/Help:Properties)   |  
| **inc_to_labels** | for each found incident from the **instance_of** query, we search for the labels in English, Italian, and Dutch. We keep it if is present in one of the languages  |
| **id_props** | we query for all properties that are descendants of [Wikidata property for an identifier](https://www.wikidata.org/wiki/Q19847637) which we discard |  
| **prop_to_labels**  | we query for all properties with their English labels  |  
| **event_type_to_labels** | for each found event type from the **subclass_of** query, we query for an English label |

For **inc_to_props**, **inc_to_labels**, and **event_type_to_labels**, we use batching using VALUES in the SPARQL queries.
There are a number of constants defined in the file. Look for the variable WDT_SPARQL_URL.

## Wikidata representation
The output of the various queries is then represented using Python classes, which 
is done by calling **wd_representation.py**. You can change the settings inside the Python module itself.
You can run [documentation.sh](scripts/documentation.sh) to create a UML diagram of the classes used.

Hardcoded settings:
* all event types must have an English label
* all properties must have an English label
* all incidents must have an English label

The most important settings are:
* **root_node**: serves as the root node in the graph. Please note that in the query **instance_of** we hardcoded the [event node](https://www.wikidata.org/wiki/Q1656682).
Anything higher than that will not work or will not have useful results.
* **needed_properties**: these are the properties that an Incident must have in order to be included
* **min_leaf_incident_freq**: the minimum number of incident that a leaf node in the directed has to have
to be accepted in the graph. If this is set to 1 or higher, all leaf nodes will be removed until there are

For event EventType, we compute:
* the frequency distribution of the Properties of the Incidents (we only indicate whether a Property is present or not in the Incident, i.e., if a Property is present multiple times, it is only added once)
* the cue validity of the Property:
    P(category|cue) = P(cat. & cue) / P(cue)

    
## Discussion
A Basic Level has two dimensions:
* **vertically**: it is most inclusive level at which categories mirror the structure perceived in the world
* **horizontally**: increased distinctiveness between categories at the same level

Properties that can aid in determining similarity between event types:
* number of incidents
* depth in the subclass of hierarchy
* frequency of each property
* cue validity of each property

 