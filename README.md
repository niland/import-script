# Niland Import Script

Usage
----
```bash
niland_importer.py --api-key YOUR_PERSONAL_API_KEY --csv-path FULL_PATH_TO_THE_CSV_FILE
```

CSV Specifications
----
### Rules ###
* The csv file must contain 11 columns per line. Leave the column blank if you have no information.
* The column separator must be `;`
* **Don't** provide the title of columns

### Columns ###
The number before the element indicates the column number.

|reference (Compulsory)|title|artist_name|album_name|popularity|duration|isrc|year|tags|audio_path|audio_url|
|-|-|-|-|-|-|-|-|-|-|
|string|string (Compulsory)|string|string|string|string|string|string|format should be: 'TagCollectionName&#124;TagName,TagCollectionName&#124;TagName,...'|Relative or absolute os path. Mandatory if no 'audio_url'|Absolute web url, Compulsory if no 'audio_path' (if both are provided, 'audio_url' used)|

Compulsory elements:
* 1 - title
* 2 - artist_name
* 9 - audio_path (relative or absolute os path)
* 10 - audio_url (absolute web url)

  You don't have to fill in both audio\_path AND audio\_url (if you do, the audio\_url will be used).

Optional elements:
* 0 - reference
* 3 - album_name
* 4 - popularity
* 5 - duration
* 6 - isrc
* 7 - year
* 8 - tags (format: `TagCollectionName|TagName,TagCollectionName|TagName,...`)
