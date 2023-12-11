# Protocol Documentation
<a name="top"></a>

## Table of Contents

- [services.proto](#services-proto)
    - [notification](#tmadmin-notification)
    - [tmrequest](#tmadmin-tmrequest)
    - [tmresponse](#tmadmin-tmresponse)
    - [tmresponse.DataEntry](#tmadmin-tmresponse-DataEntry)
  
    - [TMAdmin](#tmadmin-TMAdmin)
  
- [types_tm.proto](#types_tm-proto)
    - [Bannertype](#-Bannertype)
    - [Command](#-Command)
    - [Editors](#-Editors)
    - [Encouragingemailtype](#-Encouragingemailtype)
    - [Mappinglevel](#-Mappinglevel)
    - [Mappingnotallowed](#-Mappingnotallowed)
    - [Mappingtypes](#-Mappingtypes)
    - [Notification](#-Notification)
    - [Organizationtype](#-Organizationtype)
    - [Permissions](#-Permissions)
    - [Projectdifficulty](#-Projectdifficulty)
    - [Projectpriority](#-Projectpriority)
    - [Projectstatus](#-Projectstatus)
    - [Taskaction](#-Taskaction)
    - [Taskcreationmode](#-Taskcreationmode)
    - [Taskstatus](#-Taskstatus)
    - [Teamjoinmethod](#-Teamjoinmethod)
    - [Teammemberfunctions](#-Teammemberfunctions)
    - [Teamroles](#-Teamroles)
    - [Teamvisibility](#-Teamvisibility)
    - [Usergender](#-Usergender)
    - [Userrole](#-Userrole)
    - [Validatingnotallowed](#-Validatingnotallowed)
  
- [organizations/organizations.proto](#organizations_organizations-proto)
    - [organizations](#tmadmin-organizations)
  
- [projects/projects.proto](#projects_projects-proto)
    - [projects](#tmadmin-projects)
  
- [tasks/tasks.proto](#tasks_tasks-proto)
    - [tasks](#tmadmin-tasks)
  
- [teams/teams.proto](#teams_teams-proto)
    - [teams](#tmadmin-teams)
  
- [users/users.proto](#users_users-proto)
    - [users](#tmadmin-users)
  
- [Scalar Value Types](#scalar-value-types)



<a name="services-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## services.proto



<a name="tmadmin-notification"></a>

### notification



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| note | [Notification](#Notification) |  |  |






<a name="tmadmin-tmrequest"></a>

### tmrequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| cmd | [Command](#Command) |  |  |
| id | [int64](#int64) |  |  |
| name | [string](#string) |  |  |






<a name="tmadmin-tmresponse"></a>

### tmresponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| error_code | [int32](#int32) |  |  |
| error_msg | [string](#string) |  |  |
| data | [tmresponse.DataEntry](#tmadmin-tmresponse-DataEntry) | repeated | message Data { 	 map&lt;string, string&gt; pairs = 3; 	 } repeated Data data = 4; |






<a name="tmadmin-tmresponse-DataEntry"></a>

### tmresponse.DataEntry



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| key | [string](#string) |  |  |
| value | [string](#string) |  |  |





 

 

 


<a name="tmadmin-TMAdmin"></a>

### TMAdmin
The greeting service definition.

| Method Name | Request Type | Response Type | Description |
| ----------- | ------------ | ------------- | ------------|
| doRequest | [tmrequest](#tmadmin-tmrequest) | [tmresponse](#tmadmin-tmresponse) | These are for handling tmrequest for profile data from the database |
| doNotification | [notification](#tmadmin-notification) | [tmresponse](#tmadmin-tmresponse) |  |
| updateUserProfile | [users](#tmadmin-users) | [users](#tmadmin-users) |  |
| updateProjectProfile | [projects](#tmadmin-projects) | [projects](#tmadmin-projects) |  |
| updateTeamProfile | [teams](#tmadmin-teams) | [teams](#tmadmin-teams) |  |
| updateTask | [tasks](#tmadmin-tasks) | [tasks](#tmadmin-tasks) |  |
| updateOrganizationProfile | [organizations](#tmadmin-organizations) | [organizations](#tmadmin-organizations) |  |

 



<a name="types_tm-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## types_tm.proto


 


<a name="-Bannertype"></a>

### Bannertype


| Name | Number | Description |
| ---- | ------ | ----------- |
| INFO | 0 |  |
| WARNING | 1 |  |



<a name="-Command"></a>

### Command


| Name | Number | Description |
| ---- | ------ | ----------- |
| GET_USER | 0 |  |
| GET_ORG | 1 |  |
| GET_PROJECT | 2 |  |
| GET_TEAM | 3 |  |



<a name="-Editors"></a>

### Editors


| Name | Number | Description |
| ---- | ------ | ----------- |
| ID | 0 |  |
| JOSM | 1 |  |
| POTLATCH_2 | 2 |  |
| FIELD_PAPERS | 3 |  |
| CUSTOM | 4 |  |
| RAPID | 5 |  |



<a name="-Encouragingemailtype"></a>

### Encouragingemailtype


| Name | Number | Description |
| ---- | ------ | ----------- |
| PROJECT_PROGRESS | 0 |  |
| PROJECT_COMPLETE | 1 |  |
| BEEN_SOME_TIME | 2 |  |



<a name="-Mappinglevel"></a>

### Mappinglevel


| Name | Number | Description |
| ---- | ------ | ----------- |
| BEGINNER | 0 |  |
| INTERMEDIATE | 1 |  |
| ADVANCED | 2 |  |



<a name="-Mappingnotallowed"></a>

### Mappingnotallowed


| Name | Number | Description |
| ---- | ------ | ----------- |
| USER_ALREADY_HAS_TASK_LOCKED | 0 |  |
| USER_NOT_CORRECT_MAPPING_LEVEL | 1 |  |
| USER_NOT_ACCEPTED_LICENSE | 2 |  |
| USER_NOT_ALLOWED | 3 |  |
| PROJECT_NOT_PUBLISHED | 4 |  |
| USER_NOT_TEAM_MEMBER | 5 |  |
| PROJECT_HAS_NO_OSM_TEAM | 6 |  |
| NOT_A_MAPPING_TEAM | 7 |  |



<a name="-Mappingtypes"></a>

### Mappingtypes


| Name | Number | Description |
| ---- | ------ | ----------- |
| ROADS | 0 |  |
| BUILDINGS | 1 |  |
| WATERWAYS | 2 |  |
| LAND_USE | 3 |  |
| OTHER | 4 |  |



<a name="-Notification"></a>

### Notification


| Name | Number | Description |
| ---- | ------ | ----------- |
| BAD_DATA | 0 |  |
| BLOCKED_USER | 1 |  |
| PROJECT_FINISHED | 2 |  |



<a name="-Organizationtype"></a>

### Organizationtype


| Name | Number | Description |
| ---- | ------ | ----------- |
| FREE | 0 |  |
| DISCOUNTED | 1 |  |
| FULL_FEE | 2 |  |



<a name="-Permissions"></a>

### Permissions


| Name | Number | Description |
| ---- | ------ | ----------- |
| ANY_PERMISSIONS | 0 |  |
| LEVEL | 1 |  |
| TEAMS | 2 |  |
| TEAMS_LEVEL | 3 |  |



<a name="-Projectdifficulty"></a>

### Projectdifficulty


| Name | Number | Description |
| ---- | ------ | ----------- |
| EASY | 0 |  |
| MODERATE | 1 |  |
| CHALLENGING | 2 |  |



<a name="-Projectpriority"></a>

### Projectpriority


| Name | Number | Description |
| ---- | ------ | ----------- |
| URGENT | 0 |  |
| HIGH | 1 |  |
| MEDIUM | 2 |  |
| LOW | 3 |  |



<a name="-Projectstatus"></a>

### Projectstatus


| Name | Number | Description |
| ---- | ------ | ----------- |
| ARCHIVED | 0 |  |
| PUBLISHED | 1 |  |
| DRAFT | 2 |  |



<a name="-Taskaction"></a>

### Taskaction


| Name | Number | Description |
| ---- | ------ | ----------- |
| RELEASED_FOR_MAPPING | 0 |  |
| LOCKED_FOR_MAPPING | 1 |  |
| MARKED_MAPPED | 2 |  |
| LOCKED_FOR_VALIDATION | 3 |  |
| VALIDATED | 4 |  |
| MARKED_INVALID | 5 |  |
| MARKED_BAD | 6 |  |
| SPLIT_NEEDED | 7 |  |
| RECREATED | 8 |  |
| COMMENT | 9 |  |



<a name="-Taskcreationmode"></a>

### Taskcreationmode


| Name | Number | Description |
| ---- | ------ | ----------- |
| GRID | 0 |  |
| CREATE_ROADS | 1 |  |
| UPLOAD | 2 |  |



<a name="-Taskstatus"></a>

### Taskstatus


| Name | Number | Description |
| ---- | ------ | ----------- |
| READY | 0 |  |
| TASK_LOCKED_FOR_MAPPING | 1 |  |
| TASK_STATUS_MAPPED | 2 |  |
| TASK_LOCKED_FOR_VALIDATION | 3 |  |
| TASK_VALIDATED | 4 |  |
| TASK_INVALIDATED | 5 |  |
| BAD | 6 |  |
| SPLIT | 7 |  |
| TASK_ARCHIVED | 8 |  |



<a name="-Teamjoinmethod"></a>

### Teamjoinmethod


| Name | Number | Description |
| ---- | ------ | ----------- |
| ANY_METHOD | 0 |  |
| BY_REQUEST | 1 |  |
| BY_INVITE | 2 |  |



<a name="-Teammemberfunctions"></a>

### Teammemberfunctions


| Name | Number | Description |
| ---- | ------ | ----------- |
| MANAGER | 0 |  |
| MEMBER | 1 |  |



<a name="-Teamroles"></a>

### Teamroles


| Name | Number | Description |
| ---- | ------ | ----------- |
| TEAM_READ_ONLY | 0 |  |
| TEAM_MAPPER | 1 |  |
| VALIDATOR | 2 |  |
| PROJECT_MANAGER | 3 |  |



<a name="-Teamvisibility"></a>

### Teamvisibility


| Name | Number | Description |
| ---- | ------ | ----------- |
| PUBLIC | 0 |  |
| PRIVATE | 1 |  |



<a name="-Usergender"></a>

### Usergender


| Name | Number | Description |
| ---- | ------ | ----------- |
| MALE | 0 |  |
| FEMALE | 1 |  |
| SELF_DESCRIBE | 2 |  |
| PREFER_NOT | 3 |  |



<a name="-Userrole"></a>

### Userrole


| Name | Number | Description |
| ---- | ------ | ----------- |
| USER_READ_ONLY | 0 |  |
| USER_MAPPER | 1 |  |
| ADMIN | 2 |  |



<a name="-Validatingnotallowed"></a>

### Validatingnotallowed


| Name | Number | Description |
| ---- | ------ | ----------- |
| USER_NOT_VALIDATOR | 0 |  |
| USER_LICENSE_NOT_ACCEPTED | 1 |  |
| USER_NOT_ON_ALLOWED_LIST | 2 |  |
| PROJECT_NOT_YET_PUBLISHED | 3 |  |
| USER_IS_BEGINNER | 4 |  |
| NOT_A_VALIDATION_TEAM | 5 |  |
| USER_NOT_IN_TEAM | 6 |  |
| PROJECT_HAS_NO_TEAM | 7 |  |
| USER_ALREADY_LOCKED_TASK | 8 |  |


 

 

 



<a name="organizations_organizations-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## organizations/organizations.proto



<a name="tmadmin-organizations"></a>

### organizations



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [int64](#int64) |  |  |
| name | [string](#string) |  |  |
| slug | [string](#string) |  |  |
| logo | [string](#string) |  |  |
| description | [string](#string) |  |  |
| url | [string](#string) |  |  |
| orgtype | [Organizationtype](#Organizationtype) |  |  |





 

 

 

 



<a name="projects_projects-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## projects/projects.proto



<a name="tmadmin-projects"></a>

### projects



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [int64](#int64) |  |  |
| odkid | [int64](#int64) |  |  |
| author_id | [int64](#int64) |  |  |
| created | [google.protobuf.Timestamp](#google-protobuf-Timestamp) |  |  |
| project_name_prefix | [string](#string) |  |  |
| task_type_prefix | [string](#string) |  |  |
| location_str | [string](#string) |  |  |
| outline | [bytes](#bytes) |  |  |
| status | [Projectstatus](#Projectstatus) |  |  |
| private | [bool](#bool) |  |  |
| mapper_level | [Mappinglevel](#Mappinglevel) |  |  |
| priority | [Projectpriority](#Projectpriority) |  |  |
| centroid | [bytes](#bytes) |  |  |
| hashtags | [string](#string) | repeated |  |





 

 

 

 



<a name="tasks_tasks-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## tasks/tasks.proto



<a name="tmadmin-tasks"></a>

### tasks



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [int64](#int64) |  |  |
| project_task_name | [string](#string) |  |  |
| outline | [bytes](#bytes) |  |  |
| geometry_geojson | [string](#string) |  |  |





 

 

 

 



<a name="teams_teams-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## teams/teams.proto



<a name="tmadmin-teams"></a>

### teams



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [int64](#int64) |  |  |
| name | [string](#string) |  |  |
| logo | [string](#string) |  |  |
| description | [string](#string) |  |  |
| invite_only | [bool](#bool) |  |  |
| visibility | [Teamvisibility](#Teamvisibility) |  |  |





 

 

 

 



<a name="users_users-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## users/users.proto



<a name="tmadmin-users"></a>

### users



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [int64](#int64) |  |  |
| username | [string](#string) |  |  |
| name | [string](#string) |  |  |
| city | [string](#string) |  |  |
| country | [string](#string) |  |  |
| tasks_mapped | [int32](#int32) |  |  |
| tasks_invalidated | [int32](#int32) |  |  |
| projects_mapped | [int32](#int32) | repeated |  |
| date_registered | [google.protobuf.Timestamp](#google-protobuf-Timestamp) |  |  |
| last_validation_date | [google.protobuf.Timestamp](#google-protobuf-Timestamp) |  |  |
| password | [string](#string) |  |  |
| osm_id | [int64](#int64) |  |  |
| facebook_id | [int64](#int64) |  |  |
| irc_id | [int64](#int64) |  |  |
| skype_id | [int64](#int64) |  |  |
| slack_id | [int64](#int64) |  |  |
| linkedin_id | [int64](#int64) |  |  |
| twitter_id | [int64](#int64) |  |  |
| picture_url | [string](#string) |  |  |
| gender | [int32](#int32) |  |  |





 

 

 

 



## Scalar Value Types

| .proto Type | Notes | C++ | Java | Python | Go | C# | PHP | Ruby |
| ----------- | ----- | --- | ---- | ------ | -- | -- | --- | ---- |
| <a name="double" /> double |  | double | double | float | float64 | double | float | Float |
| <a name="float" /> float |  | float | float | float | float32 | float | float | Float |
| <a name="int32" /> int32 | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint32 instead. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="int64" /> int64 | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint64 instead. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="uint32" /> uint32 | Uses variable-length encoding. | uint32 | int | int/long | uint32 | uint | integer | Bignum or Fixnum (as required) |
| <a name="uint64" /> uint64 | Uses variable-length encoding. | uint64 | long | int/long | uint64 | ulong | integer/string | Bignum or Fixnum (as required) |
| <a name="sint32" /> sint32 | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int32s. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="sint64" /> sint64 | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int64s. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="fixed32" /> fixed32 | Always four bytes. More efficient than uint32 if values are often greater than 2^28. | uint32 | int | int | uint32 | uint | integer | Bignum or Fixnum (as required) |
| <a name="fixed64" /> fixed64 | Always eight bytes. More efficient than uint64 if values are often greater than 2^56. | uint64 | long | int/long | uint64 | ulong | integer/string | Bignum |
| <a name="sfixed32" /> sfixed32 | Always four bytes. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="sfixed64" /> sfixed64 | Always eight bytes. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="bool" /> bool |  | bool | boolean | boolean | bool | bool | boolean | TrueClass/FalseClass |
| <a name="string" /> string | A string must always contain UTF-8 encoded or 7-bit ASCII text. | string | String | str/unicode | string | string | string | String (UTF-8) |
| <a name="bytes" /> bytes | May contain any arbitrary sequence of bytes. | string | ByteString | str | []byte | ByteString | string | String (ASCII-8BIT) |

