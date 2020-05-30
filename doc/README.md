# Data-to-text data release 1.0

This folder contains the data release as described in the following publication:
```
@InProceedings{vossen-EtAl:2020:LREC,
  author    = {Vossen, Piek  and  Ilievski, Filip  and  Postma, Marten  and  Fokkens, Antske  and  Minnema, Gosse  and  Remijnse, Levi},
  title     = {Large-scale Cross-lingual Language Resources for Referencing and Framing},
  booktitle      = {Proceedings of The 12th Language Resources and Evaluation Conference},
  month          = {May},
  year           = {2020},
  address        = {Marseille, France},
  publisher      = {European Language Resources Association},
  pages     = {3162--3171},
  url       = {https://www.aclweb.org/anthology/2020.lrec-1.387}
}
```

Have you ever wondered how the same event is described in different languages? Then this dataset might be useful to you.
From [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page), we've selected 25 event types, e.g., [military operation](https://www.wikidata.org/wiki/Q645883) (see the paper Section 6 for more information).
In total, we collected 19,979 Wikidata items that belong to these 25 event types (see event_types.txt).
For each Wikidata item, we attempted to retrieve the first paragraph of the Wikipedia page describing the Wikidata item.
We included English, Italian, and Dutch texts, which we processed using various NLP systems.
Also, we represent structured data about each Wikidata item, which facilitates research into framing of events.

The dataset is available in various formats, for which we refer to the release notes in release_notes.md.
We've included one JSON file, which contains both the structured and the unstructured data, which can
be found at structured/structured_and_unstructured.json.

## Release notes
More detailed information about the data release is described in the release notes at release_notes.md.

## Licenses
* [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page) is licensed under the CC0 1.0 Universal license (CC0.md).
* [Wikipedia](https://www.wikipedia.org/) is licensed under the the CC-BY-SA-3.0 license (CC-BY-SA-3.0.md).
* all other content in this data release is licensed under the Apache 2.0 license (Apache_2.0.md).
