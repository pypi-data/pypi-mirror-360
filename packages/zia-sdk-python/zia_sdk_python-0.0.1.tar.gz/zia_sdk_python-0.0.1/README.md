
# internal-zia-python-sdk
[tbd]


# zia-python-sdk

## structure
Sdk/
    api/
    models/
    utils/
    neurolabsClient.py
    config.py
    exceptions.py

tests/
    unit/
    integration/



## more detailed look

### ApiCient
responsible for
- rest_client
- default_headers and auth

### APIs
This is responsible for interacting wth the API itself
ItemCatalog
- listCatalogItems
- createCatalogItem
- getCatalogItem
- uploadReferenceImage
- createOneFacedAsset

### StartImageRecognition
- urls
- images

### ImageRecognitionTasks
- listTasks
- createTasks
- getTask
- updateTask
- deleteTask

### ImageRecognitionResults
- getTaskResults(task_uuid)
- getIRResult(task_uuid, result_uuid)




## pain points
- Change management
- CICD and versioning of the API
- Missing functionality
    Update/Get on catalogue Items
    Variation details on catalog items
- Auth
  - add application='zia-python-sdk' to headers which we can use for logging 
- Utilities: retried and pagination
- traceability
- exception handling
- API error codes are not great currently
- configuration
- models and pydantic 
- logging



## publishing

To publish any changes you will need set poetry up with the Neurolabs API key for pypi and then run:

`poetry build`
`poetry publish`





