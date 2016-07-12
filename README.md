# Niland Import Script

Installation
----
```bash
git clone https://github.com/niland/import-script.git
cd import-script
pip install -r requirements.txt
```

Usage
----
```bash
python niland_importer.py --api-key YOUR_PERSONAL_API_KEY --csv-path FULL_PATH_TO_THE_CSV_FILE
```

CSV Specifications
----

* The column separator **must be** `;`

### Columns ###

|reference|title|artist|audio\_path|audio\_url|album|popularity|duration|isrc|year|tags|
|---------|-----|------|-----------|----------|-----|----------|--------|----|----|----|
|string\*|string\*|string\*|Relative or absolute os path. Mandatory if no audio\_url|Absolute web url, Mandatory if no audio\_path (if both are provided, audi\_path is used)|string|float|float|string|int|Format should be: TagCollectionName&#124;TagName,TagCollectionName&#124;TagName,...|

Mandatory elements (\*):
* reference
* title
* artist

You need to provide one of these elements:
* audio\_path (relative or absolute os path)
* audio\_url (absolute web url)

  You don't have to fill in both audio\_path AND audio\_url (if you do, the audio_path will be used).

All other elements are optional

For the element "tags":
* You must group similar tags under a TagCollection (Instruments, tempos, Genres, etc...)
* Try to keep your tags as consistent as possible (look for misspelling, classification errors, etc...)
* You can then add as many tags as you want for each track following this format:   `TagCollectionName|TagName,TagCollectionName|TagName,...`
