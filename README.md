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
niland_importer.py --api-key YOUR_PERSONAL_API_KEY --csv-path FULL_PATH_TO_THE_CSV_FILE
```

CSV Specifications
----

* The column separator **must be** `;`

### Columns ###

|reference|title|artist|audio_path|audio_url|album|popularity|duration|isrc|year|tags|
|-|-|-|-|-|-|-|-|-|-|
|string*|string*|string*|Relative or absolute os path. Mandatory if no 'audio_url'|Absolute web url, Mandatory if no 'audio_path' (if both are provided, 'audio_path' is used)|string|float|float|string|int|format should be: TagCollectionName&#124;TagName,TagCollectionName&#124;TagName,...|

Mandatory elements (*):
* reference
* title
* artist_name

You need to provide one of these elements:
* audio_path (relative or absolute os path)
* audio_url (absolute web url)

  You don't have to fill in both audio_path AND audio_url (if you do, the audio_path will be used).

All other elements are optional

For the element "tags":
* You must group similar tags under a TagCollection (Instruments, tempos, Genres, etc...)
* You can then add as many tags as you want for each track following this format:   `TagCollectionName|TagName,TagCollectionName|TagName,...`
