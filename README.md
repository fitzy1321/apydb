# Another Python DB Library

Basically MongoDB, but dicts and JSON and local files.

MongoDB style interface and query system, but backend by dicts objects and local JSON files in your filesystem.

I want to try optional packages orjson vs json.

And Lazy Loading.

## Example of something ...

How the json file __should__ look

file path and naming: `./[client_dir=default './data']/[database_dir_name]/[collection_name].json`

```json
{
  "docs" : [
    {"_id": 0, ...},
    {"_id": 1, ...}
  ]
}
```

## Interface

Using this series of pages to make my interface: [w3 Python Mongo](https://www.w3schools.com/python/python_mongodb_getstarted.asp)

Sections:

- [x] Create DB and Collections
- [x] "list_database_names" and "list_collection_names"
- [x] Insert into Collections
- [ ] Find in Collection
- [ ] Query
- [ ] Sort
- [ ] Delete
- [ ] Drop Collection
- [ ] Update
- [ ] Limit
