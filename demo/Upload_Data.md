## Instructions to upload Data
The following examples can be used to add some first data to the annotation tool:
- Crawl parallel web documents: 
  - Login as superuser
  - Navigate to *Data Upload* - *Crawl Web Data* and select a configuration file, e.g., `./demo/web_crawler/example_config_inclusion_europe.json`
  - in the configuration file, specify the name of the user(s) to whom the data should be assigned
  - the upload might take while because the spacy models per language are downloaded, the texts are downloaded, document-wise aligned, sentence split, tokenized and stored in the database.
  - the downloaded html files are also stored in `./data_collection/`
  - login as the user to whom the data was assigned. Navigate to *Corpora Overview* and find the uploaded data. 
- Upload non-parallel texts to simplify them:
  - Login as superuser
  - Navigate to *Data Upload* - *Upload Local Data* 
  - You're asked to enter some metadata, start for example, with the following:
    - name: "SimpleWikiHow"
    - home_page "https://www.wikihow.com/Main-Page"
    - license: CC_BY_NC_SA_4
    - to_simply: yes
    - domain: "everyday documents"
    - language: English
    - continuous text: yes
    - language level complex: C2
    - annotator: test
    - attachments: choose the files in [./demo/to_simplify](./demo/to_simplify)
  - the upload might take while because the texts are downloaded, document-wise aligned, sentence split, tokenized and stored in the database
  - login as the user to whom the data was assigned. Navigate to *Corpora Overview* and find the uploaded data.
- Upload parallel data, e.g., the golden original sentences and the simplifications generated by a TS system.
  - Please bring the data into the following format:
    - first line:  # © Origin: source_of_data [last accessed: YYYY-MM-DD]\ttitle_of_document 
      - please make sure that the title of the document changes per document, otherwise the would be assigend to the same document object in TS-ANNO
    - second_line:
      - If the data is not aligned yet: content of the document. If you want to consider paragraphs, please add "SEPL|||SEPR" between each of the paragraphs. 
      - If the data is not aligned but the text is already split into sentences, add one sentence per line. Please specify that the data is already split (pre split). You can also choose this option if you want to realign the data. 
      - If the data is already aligned: One line for each aligned text. Each line of the complex and simple file will be aligned. Please specify that the data is already aligned (pre aligned).
  - Please bring the file names into the following format:
    - complex and simple documents are aligned based on the file names, hence, *the correct file naming is important*
    - each complex file must have `.*_complex_<index>.txt` in the name
      - where `<index>` is a file id, which occurs also in the aligned simple document name
      - where `.*` can be any name 
    - each simple file must have `.*_simple_<index>.txt` in the name
      - where `<index>` is a file id, which occurs also in the aligned complex document name
      - where `.*` can be any name 
    
  - In this example, we upload the ASSET corpus to annotate rewriting strategies of the previously aligned pairs. 
  - start with downloading and bringing the data into the correct format
    - you can use the provided script for it `cd demo; bash ./demo/preprocess_asset.sh`
  - the documents are aligned based on the file names, therefore rename the files 
  - upload the data into TS-ANNO and specify the following settings:
    - name: "ASSET"
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
  - login as the user to whom the data was assigned. Navigate to *Corpora Overview* and find the uploaded data.