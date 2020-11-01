# roger

Roger is an automated graph data curation pipeline.

It transforms Knowledge Graph eXchange (KGX) files into a graph database in phases:
* **get**: Fetch KGX files from a repository.
* **merge**: Merge duplicate nodes accross multiple KGX files.
* **schema**: Infer the schema properties of nodes and edges.
* **bulk create**: Format for bulk load to Redisgraph.
* **bulk load**: Load into Redisgraph
* **validate**: Execute test queries to validate the bulk load.

## Installation

Requires Python 3.7+, Docker, and Make.

```
$ pip install requirements.txt
$ bin/roger all
```

Roger can also be run via a Makefile:
```
cd bin
make clean install
```

## Design

Each phase, in general, reads and writes a set of files.
These are managed beneath a single, configurable, root data directory.
Configuration is at roger/config.yaml.

Roger can load Redisgraph
* By running the RedisgraphTransformer (currently on a fork of KGX)
* By bulk loading Redisgraph

To build a bulk load, we
* Must ensure no duplicate nodes exist
* Preserve all properties present across duplicate nodes
* Ensure all nodes of the same type have exactly the same properties
* Generate a comprehensive header (schema) for all nodes and edges
These constraints are managed in the steps below.

### Get
Fetches KGX files according to a data version selecting the set of files to use.
### Merge
Merges nodes duplicated across files aggregating properties from all nodes
### Schema
Identify and record the schema (properties) of every edge and node type.
### Bulk Create
Create bulk load CSV files conforming to the Redisgraph Bulk Loader's requirements.
### Bulk Load
Use the bulk loader to load Redisgraph logging statistics on each type of loaded object.
### Validate
Runs a configurable list of queries with timing information to quality check the generated graph database.

## Execution

### Redisgraph

Roger uses Redisgraph's new bulk loader which is available in the 'edge' tagged Docker image.

You can run the container normally or with `/bin/bash` at the end to get a shell, like this:
```
docker run -p 6379:6379 -it --rm --name redisgraph redislabs/redisgraph:edge /bin/bash
```
This lets you have a look around inside the container. To start Redis with the graph database plugin:
```
# redis-server --loadmodule /usr/lib/redis/modules/redisgraph.so
```

A clean Roger build looks like this. Times below are on a Macbook Air.

```
$ ../bin/roger all
[roger][core.py][                 get] DEBUG: wrote                data/kgx/chembio_kgx-v0.1.json: edges:  21637 nodes:    8725 time:   13870
[roger][core.py][                 get] DEBUG: wrote     data/kgx/chemical_normalization-v0.1.json: edges: 277030 nodes:   72963 time:   15455
[roger][core.py][                 get] DEBUG: wrote          data/kgx/cord19-phenotypes-v0.1.json: edges:     24 nodes:      25 time:     392
[roger][core.py][                 get] DEBUG: wrote                        data/kgx/ctd-v0.1.json: edges:  48363 nodes:   24008 time:    7143
[roger][core.py][                 get] DEBUG: wrote                      data/kgx/foodb-v0.1.json: edges:   5429 nodes:    4536 time:    1974
[roger][core.py][                 get] DEBUG: wrote                     data/kgx/mychem-v0.1.json: edges: 123119 nodes:    5496 time:   12271
[roger][core.py][                 get] DEBUG: wrote                     data/kgx/pharos-v0.1.json: edges: 287750 nodes:  224349 time:   40150
[roger][core.py][                 get] DEBUG: wrote                     data/kgx/topmed-v0.1.json: edges:  63860 nodes:   15870 time:   10901

real	1m58.722s
user	1m4.472s
sys	0m4.625s
[roger][core.py][               merge] INFO: merging data/kgx/chembio_kgx-v0.1.json
[roger][core.py][               merge] DEBUG: merged     data/kgx/chemical_normalization-v0.1.json load: 1377 scope:     60 merge: 39
[roger][core.py][               merge] DEBUG: merged          data/kgx/cord19-phenotypes-v0.1.json load:  118 scope:     38 merge:  0
[roger][core.py][               merge] DEBUG: merged                        data/kgx/ctd-v0.1.json load: 1151 scope:     26 merge: 19
[roger][core.py][               merge] DEBUG: merged                      data/kgx/foodb-v0.1.json load:  141 scope:     24 merge:  1
[roger][core.py][               merge] DEBUG: merged                     data/kgx/mychem-v0.1.json load: 1763 scope:      9 merge:  5
[roger][core.py][               merge] DEBUG: merged                     data/kgx/pharos-v0.1.json load: 8426 scope:    218 merge:126
[roger][core.py][               merge] DEBUG: merged                     data/kgx/topmed-v0.1.json load:  873 scope:    194 merge:  4
[roger][core.py][               merge] INFO: data/kgx/chembio_kgx-v0.1.json rewrite: 1323. total merge time: 62921
[roger][core.py][               merge] INFO: merge data/merge/chemical_normalization-v0.1.json is up to date.
[roger][core.py][               merge] INFO: merge data/merge/cord19-phenotypes-v0.1.json is up to date.
[roger][core.py][               merge] INFO: merge data/merge/ctd-v0.1.json is up to date.
[roger][core.py][               merge] INFO: merge data/merge/foodb-v0.1.json is up to date.
[roger][core.py][               merge] INFO: merge data/merge/mychem-v0.1.json is up to date.
[roger][core.py][               merge] INFO: merge data/merge/pharos-v0.1.json is up to date.
[roger][core.py][               merge] INFO: merge data/merge/topmed-v0.1.json is up to date.

real	1m8.211s
user	0m53.546s
sys	0m3.894s
[roger][core.py][       is_up_to_date] DEBUG: no targets found
[roger][core.py][       create_schema] DEBUG: analyzing schema of data/kgx/chembio_kgx-v0.1.json.
[roger][core.py][       create_schema] DEBUG: analyzing schema of data/kgx/chemical_normalization-v0.1.json.
[roger][core.py][       create_schema] DEBUG: analyzing schema of data/kgx/cord19-phenotypes-v0.1.json.
[roger][core.py][       create_schema] DEBUG: analyzing schema of data/kgx/ctd-v0.1.json.
[roger][core.py][       create_schema] DEBUG: analyzing schema of data/kgx/foodb-v0.1.json.
[roger][core.py][       create_schema] DEBUG: analyzing schema of data/kgx/mychem-v0.1.json.
[roger][core.py][       create_schema] DEBUG: analyzing schema of data/kgx/pharos-v0.1.json.
[roger][core.py][       create_schema] DEBUG: analyzing schema of data/kgx/topmed-v0.1.json.
[roger][core.py][        write_schema] INFO: writing schema: data/schema/predicate-schema.json
[roger][core.py][        write_schema] INFO: writing schema: data/schema/category-schema.json

real	0m46.205s
user	0m34.701s
sys	0m3.237s
[roger][core.py][       is_up_to_date] DEBUG: no targets found
[roger][core.py][              create] INFO: processing data/merge/chembio_kgx-v0.1.json
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/nodes/chemical_substance.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/nodes/gene.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/nodes/named_thing.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/directly_interacts_with.csv
[roger][core.py][              create] INFO: processing data/merge/chemical_normalization-v0.1.json
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/similar_to.csv
[roger][core.py][              create] INFO: processing data/merge/cord19-phenotypes-v0.1.json
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/nodes/disease.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/nodes/phenotypic_feature.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/has_phenotype.csv
[roger][core.py][              create] INFO: processing data/merge/ctd-v0.1.json
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/treats.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/contributes_to.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/decreases_activity_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/decreases_molecular_interaction.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/increases_activity_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/increases_localization_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/increases_expression_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/decreases_response_to.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/increases_molecular_interaction.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/increases_degradation_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/affects_activity_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/decreases_localization_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/affects_localization_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/decreases_secretion_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/increases_secretion_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/affects_response_to.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/increases_response_to.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/increases_synthesis_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/increases_transport_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/increases_mutation_rate_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/affects_metabolic_processing_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/decreases_metabolic_processing_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/increases_metabolic_processing_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/decreases_degradation_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/affects_synthesis_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/decreases_molecular_modification_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/increases_molecular_modification_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/decreases_synthesis_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/decreases_expression_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/affects.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/decreases_stability_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/molecularly_interacts_with.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/affects_degradation_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/increases_uptake_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/decreases_mutation_rate_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/increases_stability_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/affects_expression_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/affects_secretion_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/decreases_uptake_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/affects_transport_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/decreases_transport_of.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/affects_uptake_of.csv
[roger][core.py][              create] INFO: processing data/merge/foodb-v0.1.json
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/related_to.csv
[roger][core.py][              create] INFO: processing data/merge/mychem-v0.1.json
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/causes_adverse_event.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/causes.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/Unmapped_Relation.csv
[roger][core.py][              create] INFO: processing data/merge/pharos-v0.1.json
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/gene_associated_with_condition.csv
[roger][core.py][              create] INFO: processing data/merge/topmed-v0.1.json
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/nodes/cell.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/nodes/molecular_activity.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/nodes/anatomical_entity.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/nodes/cellular_component.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/nodes/biological_process.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/association.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/has_part.csv
[roger][core.py][          write_bulk] INFO:   --creating data/bulk/edges/part_of.csv

real	1m7.897s
user	0m58.467s
sys	0m2.791s
[roger][core.py][              insert] INFO: bulk loading 
  nodes: ['data/bulk/nodes/gene.csv', 'data/bulk/nodes/molecular_activity.csv', 'data/bulk/nodes/phenotypic_feature.csv', 'data/bulk/nodes/cell.csv', 'data/bulk/nodes/biological_process.csv', 'data/bulk/nodes/chemical_substance.csv', 'data/bulk/nodes/cellular_component.csv', 'data/bulk/nodes/anatomical_entity.csv', 'data/bulk/nodes/named_thing.csv', 'data/bulk/nodes/disease.csv'] 
  edges: ['data/bulk/edges/part_of.csv', 'data/bulk/edges/decreases_metabolic_processing_of.csv', 'data/bulk/edges/decreases_uptake_of.csv', 'data/bulk/edges/decreases_secretion_of.csv', 'data/bulk/edges/decreases_molecular_modification_of.csv', 'data/bulk/edges/increases_synthesis_of.csv', 'data/bulk/edges/causes_adverse_event.csv', 'data/bulk/edges/decreases_localization_of.csv', 'data/bulk/edges/decreases_stability_of.csv', 'data/bulk/edges/treats.csv', 'data/bulk/edges/affects_activity_of.csv', 'data/bulk/edges/increases_secretion_of.csv', 'data/bulk/edges/decreases_expression_of.csv', 'data/bulk/edges/affects_transport_of.csv', 'data/bulk/edges/Unmapped_Relation.csv', 'data/bulk/edges/affects_localization_of.csv', 'data/bulk/edges/increases_stability_of.csv', 'data/bulk/edges/decreases_activity_of.csv', 'data/bulk/edges/increases_response_to.csv', 'data/bulk/edges/causes.csv', 'data/bulk/edges/decreases_degradation_of.csv', 'data/bulk/edges/similar_to.csv', 'data/bulk/edges/decreases_synthesis_of.csv', 'data/bulk/edges/affects_expression_of.csv', 'data/bulk/edges/affects_uptake_of.csv', 'data/bulk/edges/has_part.csv', 'data/bulk/edges/affects_synthesis_of.csv', 'data/bulk/edges/affects_response_to.csv', 'data/bulk/edges/increases_molecular_interaction.csv', 'data/bulk/edges/increases_localization_of.csv', 'data/bulk/edges/increases_expression_of.csv', 'data/bulk/edges/increases_uptake_of.csv', 'data/bulk/edges/related_to.csv', 'data/bulk/edges/increases_mutation_rate_of.csv', 'data/bulk/edges/affects.csv', 'data/bulk/edges/decreases_transport_of.csv', 'data/bulk/edges/gene_associated_with_condition.csv', 'data/bulk/edges/directly_interacts_with.csv', 'data/bulk/edges/increases_metabolic_processing_of.csv', 'data/bulk/edges/molecularly_interacts_with.csv', 'data/bulk/edges/increases_degradation_of.csv', 'data/bulk/edges/affects_metabolic_processing_of.csv', 'data/bulk/edges/has_phenotype.csv', 'data/bulk/edges/decreases_response_to.csv', 'data/bulk/edges/decreases_molecular_interaction.csv', 'data/bulk/edges/increases_activity_of.csv', 'data/bulk/edges/association.csv', 'data/bulk/edges/affects_secretion_of.csv', 'data/bulk/edges/decreases_mutation_rate_of.csv', 'data/bulk/edges/contributes_to.csv', 'data/bulk/edges/increases_transport_of.csv', 'data/bulk/edges/increases_molecular_modification_of.csv', 'data/bulk/edges/affects_degradation_of.csv']
[roger][core.py][              insert] INFO: deleting graph test in preparation for bulk load.
[roger][core.py][              insert] INFO: no graph to delete
[roger][core.py][              insert] INFO: bulk loading graph: test
gene  [####################################]  100%          
17868 nodes created with label 'gene'
3 nodes created with label 'molecular_activity'
phenotypic_feature  [####################################]  100%          
3723 nodes created with label 'phenotypic_feature'
8 nodes created with label 'cell'
2 nodes created with label 'biological_process'
chemical_substance  [####################################]  100%          
252966 nodes created with label 'chemical_substance'
2 nodes created with label 'cellular_component'
12 nodes created with label 'anatomical_entity'
named_thing  [####################################]  100%          
25903 nodes created with label 'named_thing'
disease  [####################################]  100%          
9777 nodes created with label 'disease'
part_of  [####################################]  100%          
31532 relations created for type 'part_of'
24 relations created for type 'decreases_metabolic_processing_of'
26 relations created for type 'decreases_uptake_of'
192 relations created for type 'decreases_secretion_of'
13 relations created for type 'decreases_molecular_modification_of'
186 relations created for type 'increases_synthesis_of'
causes_adverse_event  [####################################]  100%          
66461 relations created for type 'causes_adverse_event'
39 relations created for type 'decreases_localization_of'
12 relations created for type 'decreases_stability_of'
treats  [####################################]  100%          
11485 relations created for type 'treats'
307 relations created for type 'affects_activity_of'
527 relations created for type 'increases_secretion_of'
decreases_expression_of  [####################################]  100%
2791 relations created for type 'decreases_expression_of'
91 relations created for type 'affects_transport_of'
28 relations created for type 'Unmapped_Relation'
506 relations created for type 'affects_localization_of'
48 relations created for type 'increases_stability_of'
decreases_activity_of  [####################################]  100%          
240317 relations created for type 'decreases_activity_of'
762 relations created for type 'increases_response_to'
causes  [####################################]  100%          
46277 relations created for type 'causes'
69 relations created for type 'decreases_degradation_of'
similar_to  [####################################]  100%          
277030 relations created for type 'similar_to'
21 relations created for type 'decreases_synthesis_of'
259 relations created for type 'affects_expression_of'
19 relations created for type 'affects_uptake_of'
has_part  [####################################]  100%          
31532 relations created for type 'has_part'
42 relations created for type 'affects_synthesis_of'
1804 relations created for type 'affects_response_to'
1495 relations created for type 'increases_molecular_interaction'
119 relations created for type 'increases_localization_of'
increases_expression_of  [####################################]  100%          
4178 relations created for type 'increases_expression_of'
118 relations created for type 'increases_uptake_of'
related_to  [####################################]  100%          
5429 relations created for type 'related_to'
564 relations created for type 'increases_mutation_rate_of'
116 relations created for type 'affects'
17 relations created for type 'decreases_transport_of'
gene_associated_with_condition  [####################################]  100%          
36017 relations created for type 'gene_associated_with_condition'
directly_interacts_with  [####################################]  100%          
30826 relations created for type 'directly_interacts_with'
467 relations created for type 'increases_metabolic_processing_of'
49 relations created for type 'molecularly_interacts_with'
increases_degradation_of  [####################################]  100%
3394 relations created for type 'increases_degradation_of'
337 relations created for type 'affects_metabolic_processing_of'
24 relations created for type 'has_phenotype'
904 relations created for type 'decreases_response_to'
513 relations created for type 'decreases_molecular_interaction'
increases_activity_of  [####################################]  100%          
12061 relations created for type 'increases_activity_of'
796 relations created for type 'association'
242 relations created for type 'affects_secretion_of'
1 relations created for type 'decreases_mutation_rate_of'
contributes_to  [####################################]  100%          
16172 relations created for type 'contributes_to'
153 relations created for type 'increases_transport_of'
54 relations created for type 'increases_molecular_modification_of'
24 relations created for type 'affects_degradation_of'
Construction of graph 'test' complete: 310264 nodes created, 826470 relations created in 268.800857 seconds

real	4m31.889s
user	2m50.070s
sys	0m4.201s
config:{
  "username": "",
  "password": "",
  "host": "localhost",
  "graph": "test",
  "ports": {
    "http": 6379
  }
}
+-------------+
| b'COUNT(a)' |
+-------------+
|    310264   |
+-------------+

Cached execution 0.0
internal execution time 19.4111
[roger][core.py][            validate] INFO: Query count_nodes:Count Nodes ran in 39ms: MATCH (a) RETURN COUNT(a)
+-------------+
| b'COUNT(e)' |
+-------------+
|    826470   |
+-------------+

Cached execution 0.0
internal execution time 6.2872
[roger][core.py][            validate] INFO: Query count_edges:Count Edges ran in 14ms: MATCH (a)-[e]-(b) RETURN COUNT(e)
+-----------------+-------------------------------+
|  b'a.category'  |            b'b.id'            |
+-----------------+-------------------------------+
| ['named_thing'] |         NCBIGene:5978         |
| ['named_thing'] |           GO:0043336          |
| ['named_thing'] |          CHEBI:24433          |
| ['named_thing'] |         UBERON:0000178        |
| ['named_thing'] | TOPMED.VAR:phv00177354.v2.p10 |
| ['named_thing'] | TOPMED.VAR:phv00003307.v1.p10 |
| ['named_thing'] | TOPMED.VAR:phv00010123.v5.p10 |
...about 400 lines elided here...
| ['named_thing'] | TOPMED.VAR:phv00001046.v1.p10 |
| ['named_thing'] |  TOPMED.VAR:phv00116572.v2.p2 |
| ['named_thing'] |  TOPMED.VAR:phv00210333.v1.p1 |
| ['named_thing'] |  TOPMED.VAR:phv00307964.v1.p1 |
| ['named_thing'] |  TOPMED.VAR:phv00083411.v1.p3 |
+-----------------+-------------------------------+

Cached execution 0.0
internal execution time 656.6031
[roger][core.py][            validate] INFO: Query connectivity:TOPMED Connectivity ran in 725ms: MATCH (a { id : 'TOPMED.TAG:8' })--(b) RETURN a.category, b.id
+-----------------+--------------------------------+
|  b'a.category'  |            b'b.id'             |
+-----------------+--------------------------------+
| ['named_thing'] |         TOPMED.TAG:64          |
| ['named_thing'] | TOPMED.STUDY:phs000007.v29.p10 |
+-----------------+--------------------------------+

Cached execution 0.0
internal execution time 123.0736
[roger][core.py][            validate] INFO: Query connectivity:TOPMED Connectivity ran in 129ms: MATCH (a { id : 'TOPMED.VAR:phv00000484.v1.p10' })--(b) RETURN a.category, b.id
+-----------------+--------------------------------+
|  b'a.category'  |            b'b.id'             |
+-----------------+--------------------------------+
| ['named_thing'] |         TOPMED.TAG:30          |
| ['named_thing'] | TOPMED.STUDY:phs000007.v29.p10 |
+-----------------+--------------------------------+

Cached execution 0.0
internal execution time 111.434
[roger][core.py][            validate] INFO: Query connectivity:TOPMED Connectivity ran in 116ms: MATCH (a { id : 'TOPMED.VAR:phv00000487.v1.p10' })--(b) RETURN a.category, b.id
+-----------------+--------------------------------+
|  b'a.category'  |            b'b.id'             |
+-----------------+--------------------------------+
| ['named_thing'] |         TOPMED.TAG:74          |
| ['named_thing'] | TOPMED.STUDY:phs000007.v29.p10 |
+-----------------+--------------------------------+

Cached execution 0.0
internal execution time 110.0168
[roger][core.py][            validate] INFO: Query connectivity:TOPMED Connectivity ran in 113ms: MATCH (a { id : 'TOPMED.VAR:phv00000496.v1.p10' })--(b) RETURN a.category, b.id
+-----------------+--------------------------------+
|  b'a.category'  |            b'b.id'             |
+-----------------+--------------------------------+
| ['named_thing'] |         TOPMED.TAG:26          |
| ['named_thing'] | TOPMED.STUDY:phs000007.v29.p10 |
+-----------------+--------------------------------+

Cached execution 0.0
internal execution time 118.366
[roger][core.py][            validate] INFO: Query connectivity:TOPMED Connectivity ran in 122ms: MATCH (a { id : 'TOPMED.VAR:phv00000517.v1.p10' })--(b) RETURN a.category, b.id
+-----------------+--------------------------------+
|  b'a.category'  |            b'b.id'             |
+-----------------+--------------------------------+
| ['named_thing'] |         TOPMED.TAG:40          |
| ['named_thing'] | TOPMED.STUDY:phs000007.v29.p10 |
+-----------------+--------------------------------+

Cached execution 0.0
internal execution time 120.7783
[roger][core.py][            validate] INFO: Query connectivity:TOPMED Connectivity ran in 128ms: MATCH (a { id : 'TOPMED.VAR:phv00000518.v1.p10' })--(b) RETURN a.category, b.id
+-----------------+--------------------------------+
|  b'a.category'  |            b'b.id'             |
+-----------------+--------------------------------+
| ['named_thing'] | TOPMED.STUDY:phs000007.v29.p10 |
| ['named_thing'] |          TOPMED.TAG:7          |
+-----------------+--------------------------------+

Cached execution 0.0
internal execution time 115.9252
[roger][core.py][            validate] INFO: Query connectivity:TOPMED Connectivity ran in 120ms: MATCH (a { id : 'TOPMED.VAR:phv00000528.v1.p10' })--(b) RETURN a.category, b.id
+-----------------+--------------------------------+
|  b'a.category'  |            b'b.id'             |
+-----------------+--------------------------------+
| ['named_thing'] |          TOPMED.TAG:8          |
| ['named_thing'] | TOPMED.STUDY:phs000007.v29.p10 |
+-----------------+--------------------------------+

Cached execution 0.0
internal execution time 164.6341
[roger][core.py][            validate] INFO: Query connectivity:TOPMED Connectivity ran in 170ms: MATCH (a { id : 'TOPMED.VAR:phv00000529.v1.p10' })--(b) RETURN a.category, b.id
+-----------------+--------------------------------+
|  b'a.category'  |            b'b.id'             |
+-----------------+--------------------------------+
| ['named_thing'] | TOPMED.STUDY:phs000007.v29.p10 |
| ['named_thing'] |          TOPMED.TAG:7          |
+-----------------+--------------------------------+

Cached execution 0.0
internal execution time 137.6454
[roger][core.py][            validate] INFO: Query connectivity:TOPMED Connectivity ran in 144ms: MATCH (a { id : 'TOPMED.VAR:phv00000530.v1.p10' })--(b) RETURN a.category, b.id
+-----------------+--------------------------------+
|  b'a.category'  |            b'b.id'             |
+-----------------+--------------------------------+
| ['named_thing'] |          TOPMED.TAG:8          |
| ['named_thing'] | TOPMED.STUDY:phs000007.v29.p10 |
+-----------------+--------------------------------+

Cached execution 0.0
internal execution time 138.8376
[roger][core.py][            validate] INFO: Query connectivity:TOPMED Connectivity ran in 143ms: MATCH (a { id : 'TOPMED.VAR:phv00000531.v1.p10' })--(b) RETURN a.category, b.id
+-------------+-------------+
| b'count(a)' | b'count(b)' |
+-------------+-------------+
|   1295945   |   1295945   |
+-------------+-------------+

Cached execution 0.0
internal execution time 1661.8929
[roger][core.py][            validate] INFO: Query count_connected_nodes:Count Connected Nodes ran in 1666ms: MATCH (a)-[e]-(b) RETURN count(a), count(b)
+-----------------------+-----------------------+
| b'count(distinct(a))' | b'count(distinct(b))' |
+-----------------------+-----------------------+
|         12156         |         196144        |
+-----------------------+-----------------------+

Cached execution 0.0
internal execution time 3538.9259
[roger][core.py][            validate] INFO: Query query_by_type:Query by Type ran in 3543ms: MATCH (a:gene)-[e]-(b) WHERE 'chemical_substance' IN b.category RETURN count(distinct(a)), count(distinct(b))
```

## Airflow

This is Roger in Airflow. This is a local run. Next steps: Kubernetes.

![image](https://user-images.githubusercontent.com/306971/97792715-18dcfb80-1bb8-11eb-98d7-ea43992134de.png)

Detailed feedback for each task is available including output logs

![image](https://user-images.githubusercontent.com/306971/97792727-5fcaf100-1bb8-11eb-85b5-03cad151e0a0.png)

### Running in Airflow
In one window:
```
airflow scheduler
```
In another:
```
airflow webserver -p 8080
```
Open localhost:8080 in a browser.

Then run:
```
python tranql_translator.py
```
The Airflow interface shows the workflow:
![image](https://user-images.githubusercontent.com/306971/97787955-b968f680-1b8b-11eb-86cc-4d93842eafd3.png)

Use the Trigger icon to run the workflow immediatley.
