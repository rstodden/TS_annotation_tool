# TS-ANNO: An Annotation Tool to Build, Annotate and Evaluate Text Simplification Corpora

We introduce TS-ANNO, an open-source web application for manual creation and for evaluation of parallel corpora for text simplification (TS). 
TS-ANNO can be used for (i) sentence–wise alignment, (ii) rating alignment pairs (e.g., wrt. grammaticality, meaning preservation, ...), 
(iii) annotating alignment pairs wrt. simplification transformations (e.g., lexical substitution, sentence splitting, ...), and (iv) manual simplification of complex documents. 
For evaluation, TS-ANNO calculates inter-annotator agreement of alignments (i) and annotations (ii).

## Demo 
You can test annotation tool in our [live demo](https://ts-anno.phil.hhu.de/) (user: *test*, password: *TS_anno22*) or watch our demonstration video on YouTube.
[![Link to Youtube Video](https://i9.ytimg.com/vi/n6oJofcNjw8/mq3.jpg?sqp=CNyyv48G&rs=AOn4CLD22vwpN1a3O4mvoZoASCvDSvUKjA)](https://www.youtube.com/watch?v=n6oJofcNjw8)

## Installation

- install python3
  - if you want to use the support of the automatic simplification system MUSS, we recommend to use Python < 3.8, as MUSS is dependent on fairseq, which is yet not compatible with Python 3.9
- install packages, if you use conda install uwsgi with  `conda install -c conda-forge uwsgi` 
- install postgres
- set up postgres db with `sudo -u postgres psql`
  - `postgres=# create database demo_ts_anno with owner postgres;
  `
  - `postgres=# ALTER USER postgres WITH PASSWORD 'postgres';`
- fill database with own data
- OR use demo database `psql demo_ts_anno < demo_ts_anno.sql`

- `python manage.py makemigrations`
- `python manage.py migrate`
- `python manage.py runserver` open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser
- `python3 manage.py createsuperuser` 

Examples:
- `to align` Upload with URL: select `demo/web_crawler/config_example.json` 
- `to_simplify` select `demo/to_simplify` with the following settings: 
  - name: "SimpleWikiHow"
  - home_page https://www.wikihow.com/Main-Page"
  - license: CC_BY_NC_SA_3
  - to_simply: yes
  - domain: "everyday documents"
  - language: English
  - language level complex: C2
  - annotator: test
  - attachments: all docs of demo_corpus
- `to rate` upload ASSET (pre-aligned) to annotate and rate
  - download data  `svn checkout https://github.com/facebookresearch/asset/trunk/dataset`
  - rename data `mv dataset asset`
  - rename test and valid orig `mv asset/asset.test.orig asset/asset.test.orig.0`
  - 
  - name: "asset"
  - home_page "https://github.com/facebookresearch/asset"
  - license_file: https://raw.githubusercontent.com/facebookresearch/asset/main/LICENSE
  - domain: "wiki"
  - language: English
  - language level simple: B2
  - language level complex: C2
  - annotator: test
  - attachments: all docs of asset

## License:
The annotation tool is licensed under [GNU General Public License v3.0](https://github.com/rstodden/TS_annotation_tool/blob/master/LICENSE).

## Contact:
Feel free to contact [Regina Stodden](emailto:regina.stodden@hhu.de) if you have any comments or problems with the annotation tool.