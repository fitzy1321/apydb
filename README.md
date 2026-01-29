# Python Doc DB

My implementation of TinyDB, a local JSON Document DB.

I want to try optional packages orjson vs json.

Caching mechanism, maybe just store data locally, then when object is destructed, or contextmanager or some kind of scope, the local storage is sent to json file.

## Example of something ...

```json
{
  "collections" : {
    "[insert_name]":{
      "_last_id":0,
      "docs":{
        
      }
    }
  }
}
```
