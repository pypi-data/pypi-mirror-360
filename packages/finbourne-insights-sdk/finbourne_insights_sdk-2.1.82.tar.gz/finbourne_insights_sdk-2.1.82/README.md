<a id="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints

All URIs are relative to *https://fbn-prd.lusid.com/insights*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AccessEvaluationsApi* | [**get_access_evaluation_log**](docs/AccessEvaluationsApi.md#get_access_evaluation_log) | **GET** /api/access/{id} | [EARLY ACCESS] GetAccessEvaluationLog: Get the log for a specific access evaluation.  This endpoint will be deprecated in the near future.
*AccessEvaluationsApi* | [**list_access_evaluation_logs**](docs/AccessEvaluationsApi.md#list_access_evaluation_logs) | **GET** /api/access | [EARLY ACCESS] ListAccessEvaluationLogs: List the logs for access evaluations.
*ApplicationMetadataApi* | [**list_access_controlled_resources**](docs/ApplicationMetadataApi.md#list_access_controlled_resources) | **GET** /api/metadata/access/resources | ListAccessControlledResources: Get resources available for access control
*AuditingApi* | [**create_entry**](docs/AuditingApi.md#create_entry) | **POST** /api/auditing/entries | [EARLY ACCESS] CreateEntry: Create (persist) and audit entry..
*AuditingApi* | [**get_processes**](docs/AuditingApi.md#get_processes) | **GET** /api/auditing/processes | [EARLY ACCESS] GetProcesses: Get the latest audit entry for each process.
*AuditingApi* | [**list_entries**](docs/AuditingApi.md#list_entries) | **GET** /api/auditing/entries | [EARLY ACCESS] ListEntries: Get the audit entries.
*RequestsApi* | [**get_request**](docs/RequestsApi.md#get_request) | **GET** /api/requests/{id}/request | GetRequest: Get the request content for a specific API request.
*RequestsApi* | [**get_request_log**](docs/RequestsApi.md#get_request_log) | **GET** /api/requests/{id} | GetRequestLog: Get the log for a specific API request.
*RequestsApi* | [**get_response**](docs/RequestsApi.md#get_response) | **GET** /api/requests/{id}/response | GetResponse: Get the response for a specific API request.
*RequestsApi* | [**list_request_logs**](docs/RequestsApi.md#list_request_logs) | **GET** /api/requests | ListRequestLogs: Get the logs for API requests.
*VendorLogsApi* | [**get_vendor_log**](docs/VendorLogsApi.md#get_vendor_log) | **GET** /api/vendor/{id} | [EXPERIMENTAL] GetVendorLog: Get the log for a specific vendor request.
*VendorLogsApi* | [**get_vendor_request**](docs/VendorLogsApi.md#get_vendor_request) | **GET** /api/vendor/{id}/request | [EXPERIMENTAL] GetVendorRequest: Get the request body for a vendor request.
*VendorLogsApi* | [**get_vendor_response**](docs/VendorLogsApi.md#get_vendor_response) | **GET** /api/vendor/{id}/response | [EXPERIMENTAL] GetVendorResponse: Get the response from a vendor request.
*VendorLogsApi* | [**list_vendor_logs**](docs/VendorLogsApi.md#list_vendor_logs) | **GET** /api/vendor | [EXPERIMENTAL] ListVendorLogs: List the logs for vendor requests.


<a id="documentation-for-models"></a>
## Documentation for Models

 - [AccessControlledAction](docs/AccessControlledAction.md)
 - [AccessControlledResource](docs/AccessControlledResource.md)
 - [AccessEvaluationLog](docs/AccessEvaluationLog.md)
 - [ActionId](docs/ActionId.md)
 - [AuditData](docs/AuditData.md)
 - [AuditDataSummary](docs/AuditDataSummary.md)
 - [AuditEntry](docs/AuditEntry.md)
 - [AuditEntryNote](docs/AuditEntryNote.md)
 - [AuditProcess](docs/AuditProcess.md)
 - [AuditProcessSummary](docs/AuditProcessSummary.md)
 - [Bucket](docs/Bucket.md)
 - [CreateAuditEntry](docs/CreateAuditEntry.md)
 - [Histogram](docs/Histogram.md)
 - [IdSelectorDefinition](docs/IdSelectorDefinition.md)
 - [IdentifierPartSchema](docs/IdentifierPartSchema.md)
 - [Link](docs/Link.md)
 - [LusidProblemDetails](docs/LusidProblemDetails.md)
 - [LusidValidationProblemDetails](docs/LusidValidationProblemDetails.md)
 - [ProblemDetails](docs/ProblemDetails.md)
 - [Request](docs/Request.md)
 - [RequestLog](docs/RequestLog.md)
 - [Resource](docs/Resource.md)
 - [ResourceListOfAccessControlledResource](docs/ResourceListOfAccessControlledResource.md)
 - [ResourceListOfAuditProcessSummary](docs/ResourceListOfAuditProcessSummary.md)
 - [ResourceListWithHistogramOfAccessEvaluationLog](docs/ResourceListWithHistogramOfAccessEvaluationLog.md)
 - [ResourceListWithHistogramOfRequestLog](docs/ResourceListWithHistogramOfRequestLog.md)
 - [ResourceListWithHistogramOfVendorLog](docs/ResourceListWithHistogramOfVendorLog.md)
 - [Response](docs/Response.md)
 - [ScrollableCollectionOfAuditEntry](docs/ScrollableCollectionOfAuditEntry.md)
 - [VendorLog](docs/VendorLog.md)
 - [VendorRequest](docs/VendorRequest.md)
 - [VendorResponse](docs/VendorResponse.md)

