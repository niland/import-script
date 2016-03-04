# Niland Import Script

Usage
----
```bash
niland_importer.py --api-key YOUR_PERSONAL_API_KEY --csv-path FULL_PATH_TO_THE_CSV_FILE
```

CSV Specifications
----
### Rules ###
* The csv file must contains 11 columns per line.
* The column separator must be `;`

### Columns ###
* reference
* title
* artist_name
* album_name
* popularity
* duration
* isrc
* year
* tags (format: `TagCollectionName|TagName,TagCollectionName|TagName,...`)
* audio_path (relative or absolute os path)
* audio_url (absolute web url)

You don't have to fill in both audio\_path AND audio\_url (if you to the audio\_url will be used).
