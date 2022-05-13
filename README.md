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
  - set settings.py (or secret_files/xxx.json) with database name (_demo_ts_anno_), user name (_postgres_), and password (_postgres_) 
  - fill database with demo database `psql demo_ts_anno < demo_ts_anno.sql` OR
  - start with empty database
    - `python manage.py makemigrations`
    - `python manage.py migrate`
    - `python3 manage.py createsuperuser` 
- `python manage.py runserver` open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser
- register another user, e.g., _test_, in the interface

## Main Functionalities
### Upload Data

Examples:
- `to align` Upload with URL: select `demo/web_crawler/config_example.json` 
- `to_simplify` select `demo/to_simplify` with the following settings: 
  - name: "SimpleWikiHow"
  - home_page https://www.wikihow.com/Main-Page"
  - license: CC_BY_NC_SA_3
  - to_simply: yes
  - domain: "everyday documents"
  - language: English
  - continuous text: yes
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
  - author: Alva Manchego et al. (2020)
  - license: cc_by_nc_4
  - license_file: https://raw.githubusercontent.com/facebookresearch/asset/main/LICENSE
  - parallel: True
  - pre_aligned: True
  - to_simplify: No
  - domain: "wiki"
  - language: English
  - continuous text: no
  - language level simple: B2
  - language level complex: C2
  - annotator: test
  - attachments: all docs of asset

### Manual Sentence Alignment


### Manual Rating 
[]

### Manual Annotation of Rewriting Transformations

### Simplification
<img src="https://github.com/stodden/TS_annotation_tool/blob/master/demo/simplification.png">

### ToDo:
- start with running the annotation tool on a local server to receive possible issues. If you are running the deployment mode, you only receive "Server Error (500)" without any relevant infromation on the error. 

## License:
The annotation tool is licensed under [GNU General Public License v3.0](https://github.com/rstodden/TS_annotation_tool/blob/master/LICENSE).

## Citation

If you use TS-anno in your research, please cite our paper:

```
@inproceedings{stodden-kallmeyer-2022-ts-anno,
    title = "{TS-ANNO}: An Annotation Tool to Build, Annotate and Evaluate Text
Simplification Corpora",
    author = "Stodden, Regina and Kallmeyer, Laura",
    booktitle = "Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics: System Demonstrations",
    month = may,
    year = "2022",
    address = "Ireland, Dublin",
    publisher = "Association for Computational Linguistics"
}
```
## Contact:
Feel free to contact [Regina Stodden](emailto:regina.stodden@hhu.de) if you have any comments or problems with the annotation tool.