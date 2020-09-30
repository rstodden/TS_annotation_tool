# ToDo
- compare other rating forms with the one ASSET. So far ASSET's version is implemented using a continuous scale from 0 to 100
- add different translations https://docs.djangoproject.com/en/3.1/topics/i18n/translation/
- time used for rating and alignment, fields in model already created (created_at, updates_at, finished_at, duration)

## Install
### Dependencies
- python3
- requirements.txt `pip3 install -r requirements.txt`


## Structure
The django project has different apps:
- TS_annotation_tool: global directory for all apps
- alignment: aligning the documents
- rating: rating the alignment pairs
- evaluation: for admin only to export data and generate inter-annotator-agreement