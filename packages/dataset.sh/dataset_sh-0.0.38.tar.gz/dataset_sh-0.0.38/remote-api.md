```typescript

// upload new dataet version
// POST    /api/dataset/{owner}/{dataset_name}
// Request Body:
// Response:
// Code: 204
// Empty


// get dataset readme
// GET     /api/dataset/{owner}/{dataset_name}/readme
// Response:
string

// set dataset readme
// POST    /api/dataset/{owner}/{dataset_name}/readme
// Request Body:
{
    readme: string
}
// Response:
// 204

// list all version tags
// GET     /api/dataset/{owner}/{dataset_name}/tag
// Response:
{
    items: {
        version: string,
        tag: string
    }[]
}

// tag a dataset version
// POST    /api/dataset/{owner}/{dataset_name}/tag/{tag}
// Request Body:
{
    version: string
}
// Response:
// 204

// untag version
// DELETE  /api/dataset/{owner}/{dataset_name}/tag/{tag}
// Request:
// Response:
// 204

// get version tag information
// GET  /api/dataset/{owner}/{dataset_name}/tag/{tag}
// Request:
// Response:
{
    version: string,
    tag: string
}

// download by tag name
// GET     /api/dataset/{owner}/{dataset_name}/tag/{tag}/file
// Request:
// Response:

// list versions
// GET     /api/dataset/{owner}/{dataset_name}/version
// Request:
// Response:
{
    items: {
        version: string, 
        fileSize: number,
        description?: string            
        createdAt: number // seconds since epoch.
    }[]
}
// delete version
// DELETE  /api/dataset/{owner}/{dataset_name}/version/{version}
// Request:
// Response:

// download by version
// GET     /api/dataset/{owner}/{dataset_name}/version/{version}/file
// Request: 
// Response:

```