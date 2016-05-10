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

### Columns ###
The number before the element indicates the column number.

Compulsory elements:
1. title
2. artist_name
9. audio_path (relative or absolute os path)
10. audio_url (absolute web url)

  You don't have to fill in both audio\_path AND audio\_url (if you do, the audio\_url will be used).
  
Optional elements:
0. reference
3. album_name
4. popularity
5. duration
6. isrc
7. year
8. tags (format: `TagCollectionName|TagName,TagCollectionName|TagName,...`)



