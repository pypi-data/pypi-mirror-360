#   Copyright 2023 Dynatrace LLC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

# DO NOT EDIT, this is an Auto-generated file from ./templates/python_constants.py.j2

from enum import Enum

__version__ = "0.36.0.20230313.110629"
"""Artifact Version
"""

CLOUD_PREFIX = "cloud"
"""Prefix for 'cloud'
"""

CONTAINER_PREFIX = "container"
"""Prefix for 'container'
"""

DT_CLOUD_GCP_PREFIX = "gcp"
"""Prefix for 'dt.cloud.gcp'
"""

DT_CTG_RESOURCE_PREFIX = "dt.ctg"
"""Prefix for 'dt.ctg_resource'
"""

DT_ENV_VARS_PREFIX = "dt.env_vars"
"""Prefix for 'dt.env_vars'
"""

DT_FAAS_RESOURCE_PREFIX = "dt.faas"
"""Prefix for 'dt.faas_resource'
"""

DT_IMS_RESOURCE_PREFIX = "dt.ims"
"""Prefix for 'dt.ims_resource'
"""

DT_OS_PREFIX = "dt.os"
"""Prefix for 'dt.os'
"""

DT_OSI_PREFIX = "dt.host"
"""Prefix for 'dt.osi'
"""

DT_PGI_PREFIX = "dt.process"
"""Prefix for 'dt.pgi'
"""

DT_TECH_PREFIX = "dt.tech"
"""Prefix for 'dt.tech'
"""

DT_TELEMETRY_EXPORTER_PREFIX = "telemetry.exporter"
"""Prefix for 'dt.telemetry.exporter'
"""

DT_WEBSPHERE_PREFIX = "dt.websphere"
"""Prefix for 'dt.websphere'
"""

DT_ZOSCONNECT_RESOURCE_PREFIX = "dt.zosconnect"
"""Prefix for 'dt.zosconnect_resource'
"""

FAAS_RESOURCE_PREFIX = "faas"
"""Prefix for 'faas_resource'
"""

HOST_PREFIX = "host"
"""Prefix for 'host'
"""

PROCESS_PREFIX = "process"
"""Prefix for 'process'
"""

PROCESS_EXECUTABLE_PREFIX = "process.executable"
"""Prefix for 'process.executable'
"""

PROCESS_RUNTIME_PREFIX = "process.runtime"
"""Prefix for 'process.runtime'
"""

SERVICE_PREFIX = "service"
"""Prefix for 'service'
"""

TELEMETRY_SDK_PREFIX = "telemetry.sdk"
"""Prefix for 'telemetry.sdk'
"""

AWS_LAMBDA_PREFIX = "aws.lambda"
"""Prefix for 'aws.lambda'
"""

CODE_PREFIX = "code"
"""Prefix for 'code'
"""

DB_PREFIX = "db"
"""Prefix for 'db'
"""

DB_MSSQL_PREFIX = "db.mssql"
"""Prefix for 'db.mssql'
"""

DB_CASSANDRA_PREFIX = "db.cassandra"
"""Prefix for 'db.cassandra'
"""

DB_HBASE_PREFIX = "db.hbase"
"""Prefix for 'db.hbase'
"""

DB_REDIS_PREFIX = "db.redis"
"""Prefix for 'db.redis'
"""

DB_MONGODB_PREFIX = "db.mongodb"
"""Prefix for 'db.mongodb'
"""

DT_DB_PREFIX = "dt.db"
"""Prefix for 'dt.db'
"""

DT_EXCEPTION_PREFIX = "dt.exception"
"""Prefix for 'dt.exception'
"""

DT_CODE_PREFIX = "dt.code"
"""Prefix for 'dt.code'
"""

DT_STACKTRACE_PREFIX = "dt.stacktrace"
"""Prefix for 'dt.stacktrace'
"""

DT_HTTP_SERVER_PREFIX = "dt.http"
"""Prefix for 'dt.http.server'
"""

OTEL_LIBRARY_PREFIX = "otel.library"
"""Prefix for 'otel.library'
"""

DT_MESSAGING_PREFIX = "dt.messaging"
"""Prefix for 'dt.messaging'
"""

DT_PARENT_PREFIX = "dt.parent"
"""Prefix for 'dt.parent'
"""

DT_RUM_PREFIX = "dt.rum"
"""Prefix for 'dt.rum'
"""

FAAS_SPAN_DATASOURCE_PREFIX = "faas.document"
"""Prefix for 'faas_span.datasource'
"""

NETWORK_PREFIX = "net"
"""Prefix for 'network'
"""

IDENTITY_PREFIX = "enduser"
"""Prefix for 'identity'
"""

HTTP_PREFIX = "http"
"""Prefix for 'http'
"""

AWS_PREFIX = "aws"
"""Prefix for 'aws'
"""


DYNAMODB_SHARED_PREFIX = "aws.dynamodb"
"""Prefix for 'dynamodb.shared'
"""

MESSAGING_PREFIX = "messaging"
"""Prefix for 'messaging'
"""

RPC_PREFIX = "rpc"
"""Prefix for 'rpc'
"""

RPC_GRPC_PREFIX = "rpc.grpc"
"""Prefix for 'rpc.grpc'
"""

RPC_JSONRPC_PREFIX = "rpc.jsonrpc"
"""Prefix for 'rpc.jsonrpc'
"""

RPC_MESSAGE_PREFIX = "message"
"""Prefix for 'rpc.message'
"""



CLOUD_PROVIDER = "cloud.provider"
"""Name of the cloud provider.
This attribute expects a value of type string from the enumeration CloudProviderValues.
"""

CLOUD_ACCOUNT_ID = "cloud.account.id"
"""The cloud account ID the resource is assigned to.
This attribute expects a value of type string.
"""

CLOUD_REGION = "cloud.region"
"""The geographical region the resource is running. Refer to your provider's docs to see the available regions, for example [AWS regions](https://aws.amazon.com/about-aws/global-infrastructure/regions_az/), [Azure regions](https://azure.microsoft.com/en-us/global-infrastructure/geographies/), or [Google Cloud regions](https://cloud.google.com/about/locations).
This attribute expects a value of type string.
"""

CLOUD_AVAILABILITY_ZONE = "cloud.availability_zone"
"""Cloud regions often have multiple, isolated locations known as zones to increase availability. Availability zone represents the zone where the resource is running.
This attribute expects a value of type string.

Note: Availability zones are called "zones" on Google Cloud.
"""

CLOUD_PLATFORM = "cloud.platform"
"""The cloud platform in use.
This attribute expects a value of type string from the enumeration CloudPlatformValues.

Note: The prefix of the service SHOULD match the one specified in `cloud.provider`.
"""

CONTAINER_NAME = "container.name"
"""Container name.
This attribute expects a value of type string.
"""

CONTAINER_IMAGE_NAME = "container.image.name"
"""Name of the image the container was built on.
This attribute expects a value of type string.
"""

CONTAINER_IMAGE_TAG = "container.image.tag"
"""Container image tag.
This attribute expects a value of type string.
"""

GCP_PROJECT_ID = "gcp.project.id"
"""A project organizes all your Google Cloud resources.
This attribute expects a value of type string.
"""

GCP_REGION = "gcp.region"
"""A region is a specific geographical location where you can host your resources.
This attribute expects a value of type string.
"""

GCP_INSTANCE_ID = "gcp.instance.id"
"""A permanent identifier that is unique within your Google Cloud project.
This attribute expects a value of type string.
"""

GCP_INSTANCE_NAME = "gcp.instance.name"
"""The name to display for the instance in the Cloud Console.
This attribute expects a value of type string.
"""

GCP_RESOURCE_TYPE = "gcp.resource.type"
"""The name of a resource type.
This attribute expects a value of type string.
"""

DT_CTG_DETECTED = "dt.ctg.detected"
"""True if the agent is running in a IBM CTG process. Not set otherwise.
This attribute expects a value of type boolean.

.. deprecated::
   Use `dt.tech.agent_detected_main_technology` instead.
"""

DT_ENV_VARS_DT_CUSTOM_PROP = "dt.env_vars.dt_custom_prop"
"""Reports the value of the `DT_CUSTOM_PROP` environment variable as described [here](https://www.dynatrace.com/support/help/how-to-use-dynatrace/process-groups/configuration/define-your-own-process-group-metadata/).
This attribute expects a value of type string.
"""

DT_ENV_VARS_DT_TAGS = "dt.env_vars.dt_tags"
"""Reports the value of the `DT_TAGS` environment variable as described [here](https://www.dynatrace.com/support/help/how-to-use-dynatrace/tags-and-metadata/setup/define-tags-based-on-environment-variables/).
This attribute expects a value of type string.
"""

DT_FAAS_AWS_INITIALIZATION_TYPE = "dt.faas.aws.initialization_type"
"""The AWS Lambda initialization type (see [AWS_LAMBDA_INITIALIZATION_TYPE environment variable](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html#configuration-envvars-runtime)).
This attribute expects a value of type string from the enumeration DtFaasAwsInitializationTypeValues.

Note: This is especially interesting for runtimes supporting [SnapStart](https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html) (currently only Java).
"""

DT_IMS_DETECTED = "dt.ims.detected"
"""True if the agent is running in an IMS SOAP gateway process. Not set otherwise.
This attribute expects a value of type boolean.

.. deprecated::
   Use `dt.tech.agent_detected_main_technology` instead.
"""

DT_OS_TYPE = "dt.os.type"
"""The operating system type.
This attribute expects a value of type string from the enumeration DtOsTypeValues.
"""

DT_OS_DESCRIPTION = "dt.os.description"
"""Human readable (not intended to be parsed) OS version information, like e.g. reported by `ver` or `lsb_release -a` commands.
This attribute expects a value of type string.
"""

DT_HOST_SNAID = "dt.host.snaid"
"""The SNA ID is the Systems Network Architecture (SNA) identifier. It's a unique ID for a given IP address on the network. In combination with the calculated OSI, this is required to calculate the PGI.
This attribute expects a value of type string.
"""

DT_HOST_SMFID = "dt.host.smfid"
"""The SMF ID is the name of the LPAR (logical partition), which is a "host" as far as Dynatrace is concerned. In combination with the IP address, this is required to calculate the OSI.
This attribute expects a value of type string.
"""

DT_HOST_IP = "dt.host.ip"
"""Similar to net.host.ip for spans. Currently, there is no OpenTelemetry convention for IP addresses on resources.
This attribute expects a value of type string.
"""

DT_PROCESS_EXECUTABLE = "dt.process.executable"
"""The path to the executable.
This attribute expects a value of type string.
"""

DT_PROCESS_COMMANDLINE = "dt.process.commandline"
"""The command line arguments of the process as a string.
This attribute expects a value of type string.

Note: Ideally, this is the original "raw" command line including the executable path, but this might not be possible in all frameworks. In such cases, this can be a best-effort recreation of the commandline. Examples are truncated for readability.
"""

DT_PROCESS_PID = "dt.process.pid"
"""Process ID (PID) the data belongs to.
This attribute expects a value of type string.
"""

DT_PROCESS_ZOS_JOB_NAME = "dt.process.zos_job_name"
"""The z/OS job name of the process.
This attribute expects a value of type string.
"""

DT_TECH_AGENT_DETECTED_MAIN_TECHNOLOGY = "dt.tech.agent_detected_main_technology"
"""The main technology the agent has detected.
This attribute expects a value of type string from the enumeration DtTechAgentDetectedMainTechnologyValues.
"""

TELEMETRY_EXPORTER_NAME = "telemetry.exporter.name"
"""The exporter name. MUST be `odin` for ODIN protocol.
This attribute expects a value of type string from the enumeration TelemetryExporterNameValues.
"""

TELEMETRY_EXPORTER_VERSION = "telemetry.exporter.version"
"""The full agent/exporter version.
This attribute expects a value of type string.
"""

TELEMETRY_EXPORTER_PACKAGE_VERSION = "telemetry.exporter.package_version"
"""The version as exposed to the package manager-.
This attribute expects a value of type string.

Note: Many package managers won't accept the sprint + timestamp version format as required for `version` if `name` is `odin` but instead need a semver-compatible string with the intended meaning (for example, the `-` used in the sprint version indicates a pre-release version). That package version MAY be provided in this informational attribute.
"""

DT_WEBSPHERE_SERVER_NAME = "dt.websphere.server_name"
"""Name of the WebSphere server.
This attribute expects a value of type string.
"""

DT_WEBSPHERE_NODE_NAME = "dt.websphere.node_name"
"""Name of the WebSphere node the application is running on.
This attribute expects a value of type string.
"""

DT_WEBSPHERE_CELL_NAME = "dt.websphere.cell_name"
"""Name of the WebSphere cell the application is running in.
This attribute expects a value of type string.
"""

DT_WEBSPHERE_CLUSTER_NAME = "dt.websphere.cluster_name"
"""Name of the WebSphere cluster the application is running in.
This attribute expects a value of type string.
"""

DT_ZOSCONNECT_DETECTED = "dt.zosconnect.detected"
"""Set to true if the agent is running in a z/OS Connect EE server process.
This attribute expects a value of type boolean.

Note: This value is normally either unset or `true`.

.. deprecated::
   Use `dt.tech.agent_detected_main_technology` instead.
"""

FAAS_NAME = "faas.name"
"""The name of the single function that this runtime instance executes.
This attribute expects a value of type string.

Note: This is the name of the function as configured/deployed on the FaaS platform and is usually different from the name of the callback function (which may be stored in the [`code.namespace`/`code.function`](../../trace/semantic_conventions/span-general.md#source-code-attributes) span attributes).
"""

FAAS_ID = "faas.id"
"""The unique ID of the single function that this runtime instance executes.
This attribute expects a value of type string.

Note: Depending on the cloud provider, use:

* **AWS Lambda:** The function [ARN](https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html).
Take care not to use the "invoked ARN" directly but replace any
[alias suffix](https://docs.aws.amazon.com/lambda/latest/dg/configuration-aliases.html) with the resolved function version, as the same runtime instance may be invokable with multiple
different aliases.
* **GCP:** The [URI of the resource](https://cloud.google.com/iam/docs/full-resource-names)
* **Azure:** The [Fully Qualified Resource ID](https://docs.microsoft.com/en-us/rest/api/resources/resources/get-by-id).

On some providers, it may not be possible to determine the full ID at startup,
which is why this field cannot be made required. For example, on AWS the account ID
part of the ARN is not available without calling another AWS API
which may be deemed too slow for a short-running lambda function.
As an alternative, consider setting `faas.id` as a span attribute instead.
"""

FAAS_VERSION = "faas.version"
"""The immutable version of the function being executed.
This attribute expects a value of type string.

Note: Depending on the cloud provider and platform, use:

* **AWS Lambda:** The [function version](https://docs.aws.amazon.com/lambda/latest/dg/configuration-versions.html)
  (an integer represented as a decimal string).
* **Google Cloud Run:** The [revision](https://cloud.google.com/run/docs/managing/revisions)
  (i.e., the function name plus the revision suffix).
* **Google Cloud Functions:** The value of the
  [`K_REVISION` environment variable](https://cloud.google.com/functions/docs/env-var#runtime_environment_variables_set_automatically).
* **Azure Functions:** Not applicable. Do not set this attribute.
"""

FAAS_INSTANCE = "faas.instance"
"""The execution environment ID as a string, that will be potentially reused for other invocations to the same function/function version.
This attribute expects a value of type string.

Note: * **AWS Lambda:** Use the (full) log stream name.
"""

FAAS_MAX_MEMORY = "faas.max_memory"
"""The amount of memory available to the serverless function in MiB.
This attribute expects a value of type int.

Note: It's recommended to set this attribute since e.g. too little memory can easily stop a Java AWS Lambda function from working correctly. On AWS Lambda, the environment variable `AWS_LAMBDA_FUNCTION_MEMORY_SIZE` provides this information.
"""

HOST_HOSTNAME = "host.hostname"
"""Hostname of the host. It contains what the `hostname` command returns on the host machine.
This attribute expects a value of type string.

.. deprecated::
   Deprecated. Use attribute `host.name` instead.
"""

HOST_ID = "host.id"
"""Unique host id.
This attribute expects a value of type string.

Note: For Cloud this must be the instance_id assigned by the cloud provider.
"""

HOST_NAME = "host.name"
"""Name of the host. It may contain what `hostname` returns on Unix systems, the fully qualified, or a name specified by the user.
This attribute expects a value of type string.
"""

HOST_TYPE = "host.type"
"""Type of host.
This attribute expects a value of type string.

Note: For Cloud this must be the machine type.
"""

HOST_IMAGE_NAME = "host.image.name"
"""Name of the VM image or OS install the host was instantiated from.
This attribute expects a value of type string.
"""

HOST_IMAGE_ID = "host.image.id"
"""VM image id.
This attribute expects a value of type string.

Note: For Cloud, this value is from the provider.
"""

HOST_IMAGE_VERSION = "host.image.version"
"""The version string of the VM image as defined in [Version Attributes](https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/resource/semantic_conventions#version-attributes).
This attribute expects a value of type string.
"""

HOST_ARCH = "host.arch"
"""The CPU architecture the host system is running on.
This attribute expects a value of type string from the enumeration HostArchValues.
"""

PROCESS_PID = "process.pid"
"""Process identifier (PID).
This attribute expects a value of type int.
"""

PROCESS_OWNER = "process.owner"
"""The username of the user that owns the process.
This attribute expects a value of type string.
"""

PROCESS_COMMAND = "process.command"
"""The command used to launch the process (i.e. the command name). On Linux based systems, can be set to the zeroth string in `proc/[pid]/cmdline`. On Windows, can be set to the first parameter extracted from `GetCommandLineW`.
This attribute expects a value of type string.
"""

PROCESS_COMMAND_LINE = "process.command_line"
"""The full command used to launch the process. The value can be either a list of strings representing the ordered list of arguments, or a single string representing the full command. On Linux based systems, can be set to the list of null-delimited strings extracted from `proc/[pid]/cmdline`. On Windows, can be set to the result of `GetCommandLineW`.
This attribute expects a value of type string[].

Note: Union types are not yet supported, so instead of `string` a single-element array is used.
"""

PROCESS_EXECUTABLE_NAME = "process.executable.name"
"""The name of the process executable. On Linux based systems, can be set to the `Name` in `proc/[pid]/status`. On Windows, can be set to the base name of `GetProcessImageFileNameW`.
This attribute expects a value of type string.
"""

PROCESS_EXECUTABLE_PATH = "process.executable.path"
"""The full path to the process executable. On Linux based systems, can be set to the target of `proc/[pid]/exe`. On Windows, can be set to the result of `GetProcessImageFileNameW`.
This attribute expects a value of type string.
"""

PROCESS_RUNTIME_NAME = "process.runtime.name"
"""The name of the runtime of this process.
This attribute expects a value of type string from the enumeration ProcessRuntimeNameValues.

Note: SHOULD be set to one of the values listed below, unless more detailed instructions are provided. If none of the listed values apply, a custom value best describing the runtime CAN be used. For compiled native binaries, this SHOULD be the name of the compiler.
"""

PROCESS_RUNTIME_VERSION = "process.runtime.version"
"""The version of the runtime of this process, as returned by the runtime without modification.
This attribute expects a value of type string.
"""

PROCESS_RUNTIME_DESCRIPTION = "process.runtime.description"
"""An additional description about the runtime of the process, for example a specific vendor customization of the runtime environment.
This attribute expects a value of type string.
"""

SERVICE_NAME = "service.name"
"""Logical name of the service.
This attribute expects a value of type string.

Note: MUST be the same for all instances of horizontally scaled services.
"""

SERVICE_NAMESPACE = "service.namespace"
"""A namespace for `service.name`.
This attribute expects a value of type string.

Note: A string value having a meaning that helps to distinguish a group of services, for example the team name that owns a group of services. `service.name` is expected to be unique within the same namespace. The field is optional. If `service.namespace` is not specified in the Resource then `service.name` is expected to be unique for all services that have no explicit namespace defined (so the empty/unspecified namespace is simply one more valid namespace). Zero-length namespace string is assumed equal to unspecified namespace.
"""

SERVICE_INSTANCE_ID = "service.instance.id"
"""The string ID of the service instance.
This attribute expects a value of type string.

Note: MUST be unique for each instance of the same `service.namespace,service.name` pair (in other words `service.namespace,service.name,service.id` triplet MUST be globally unique). The ID helps to distinguish instances of the same service that exist at the same time (e.g. instances of a horizontally scaled service). It is preferable for the ID to be persistent and stay the same for the lifetime of the service instance, however it is acceptable that the ID is ephemeral and changes during important lifetime events for the service (e.g. service restarts). If the service has no inherent unique ID that can be used as the value of this attribute it is recommended to generate a random Version 1 or Version 4 RFC 4122 UUID (services aiming for reproducible UUIDs may also use Version 5, see RFC 4122 for more recommendations).
"""

SERVICE_VERSION = "service.version"
"""The version string of the service API or implementation as defined in [Version Attributes](https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/resource/semantic_conventions#version-attributes).
This attribute expects a value of type string.
"""

TELEMETRY_SDK_NAME = "telemetry.sdk.name"
"""The name of the telemetry SDK as defined above.
This attribute expects a value of type string.

Note: The default OpenTelemetry SDK provided by the OpenTelemetry project MUST set `telemetry.sdk.name` to the value opentelemetry. If another SDK, like a fork or a vendor-provided implementation, is used, this SDK MUST set the attribute `telemetry.sdk.name` to the fully-qualified class or module name of this SDK's main entry point or another suitable identifier depending on the language. The identifier `opentelemetry` is reserved and MUST NOT be used in this case. The identifier SHOULD be stable across different versions of an implementation.
"""

TELEMETRY_SDK_LANGUAGE = "telemetry.sdk.language"
"""The language of the telemetry SDK.
This attribute expects a value of type string from the enumeration TelemetrySdkLanguageValues.
"""

TELEMETRY_SDK_VERSION = "telemetry.sdk.version"
"""The version string of the service API or implementation as defined in [Version Attributes](https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/resource/semantic_conventions#version-attributes).
This attribute expects a value of type string.
"""

AWS_LAMBDA_INVOKED_ARN = "aws.lambda.invoked_arn"
"""The full invoked ARN as provided on the `Context` passed to the function (`Lambda-Runtime-Invoked-Function-Arn` header on the `/runtime/invocation/next` applicable).
This attribute expects a value of type string.

Note: This may be different from `faas.id` if an alias is involved.
"""

CODE_FUNCTION = "code.function"
"""The method or function name, or equivalent (usually rightmost part of the code unit's name).
This attribute expects a value of type string.
"""

CODE_NAMESPACE = "code.namespace"
"""The "namespace" within which `code.function` is defined. Usually the qualified class or module name, such that `code.namespace` + some separator + `code.function` form a unique identifier for the code unit.
This attribute expects a value of type string.
"""

CODE_FILEPATH = "code.filepath"
"""The source code file name that identifies the code unit as uniquely as possible (preferably an absolute file path).
This attribute expects a value of type string.
"""

CODE_LINENO = "code.lineno"
"""The line number in `code.filepath` best representing the operation. It SHOULD point within the code unit named in code.function.
This attribute expects a value of type int.
"""

DB_SYSTEM = "db.system"
"""An identifier for the database management system (DBMS) product being used. See below for a list of well-known identifiers.
This attribute expects a value of type string from the enumeration DbSystemValues.
"""

DB_CONNECTION_STRING = "db.connection_string"
"""The connection string used to connect to the database.
This attribute expects a value of type string.

Note: It is recommended to remove embedded credentials.
"""

DB_USER = "db.user"
"""Username for accessing the database.
This attribute expects a value of type string.
"""

DB_JDBC_DRIVER_CLASSNAME = "db.jdbc.driver_classname"
"""The fully-qualified class name of the [Java Database Connectivity (JDBC)](https://docs.oracle.com/javase/8/docs/technotes/guides/jdbc/) driver used to connect.
This attribute expects a value of type string.
"""

DB_NAME = "db.name"
"""If no tech-specific attribute is defined, this attribute is used to report the name of the database being accessed. For commands that switch the database, this should be set to the target database (even if the command fails).
This attribute expects a value of type string.

Note: In some SQL databases, the database name to be used is called "schema name".
"""

DB_STATEMENT = "db.statement"
"""The database statement being executed.
This attribute expects a value of type string.

Note: The value may be sanitized to exclude sensitive information.
"""

DB_OPERATION = "db.operation"
"""The name of the operation being executed, e.g. the [MongoDB command name](https://docs.mongodb.com/manual/reference/command/#database-operations) such as `findAndModify`.
This attribute expects a value of type string.

Note: While it would semantically make sense to set this, e.g., to a SQL keyword like `SELECT` or `INSERT`, it is not recommended to attempt any client-side parsing of `db.statement` just to get this property (the back end can do that if required).
"""

NET_PEER_NAME = "net.peer.name"
"""Remote hostname or similar, see note below.
This attribute expects a value of type string.
"""

NET_PEER_IP = "net.peer.ip"
"""Remote address of the peer (dotted decimal for IPv4 or [RFC5952](https://rfc-editor.org/rfc/rfc5952) for IPv6).
This attribute expects a value of type string.
"""

NET_PEER_PORT = "net.peer.port"
"""Remote port number.
This attribute expects a value of type int.
"""

NET_TRANSPORT = "net.transport"
"""Transport protocol used. See note below.
This attribute expects a value of type string from the enumeration NetTransportValues.
"""

DB_MSSQL_INSTANCE_NAME = "db.mssql.instance_name"
"""The Microsoft SQL Server [instance name](https://docs.microsoft.com/en-us/sql/connect/jdbc/building-the-connection-url?view=sql-server-ver15) connecting to. This name is used to determine the port of a named instance.
This attribute expects a value of type string.

Note: If setting a `db.mssql.instance_name`, `net.peer.port` is no longer required (but still recommended if non-standard).
"""

DB_CASSANDRA_KEYSPACE = "db.cassandra.keyspace"
"""The name of the keyspace being accessed. To be used instead of the generic `db.name` attribute.
This attribute expects a value of type string.
"""

DB_HBASE_NAMESPACE = "db.hbase.namespace"
"""The [HBase namespace](https://hbase.apache.org/book.html#_namespace) being accessed. To be used instead of the generic `db.name` attribute.
This attribute expects a value of type string.
"""

DB_REDIS_DATABASE_INDEX = "db.redis.database_index"
"""The index of the database being accessed as used in the [`SELECT` command](https://redis.io/commands/select), provided as an integer. To be used instead of the generic `db.name` attribute.
This attribute expects a value of type int.
"""

DB_MONGODB_COLLECTION = "db.mongodb.collection"
"""The collection being accessed within the database stated in `db.name`.
This attribute expects a value of type string.
"""

DT_CTG_GATEWAYURL = "dt.ctg.gatewayurl"
"""URL of the gateway.
This attribute expects a value of type string.
"""

DT_CTG_REQUESTTYPE = "dt.ctg.requesttype"
"""Type of the CTG GatewayRequest.
This attribute expects a value of type string from the enumeration DtCtgRequesttypeValues.
"""

DT_CTG_CALLTYPE = "dt.ctg.calltype"
"""Integer representing the specific calltype of the CTG GatewayRequest.
This attribute expects a value of type int from the enumeration DtCtgCalltypeValues.
"""

DT_CTG_SERVERID = "dt.ctg.serverid"
"""ID/name of the server.
This attribute expects a value of type string.
"""

DT_CTG_USERID = "dt.ctg.userid"
"""ID/name of the user.
This attribute expects a value of type string.
"""

DT_CTG_TRANSID = "dt.ctg.transid"
"""ID of the transaction.
This attribute expects a value of type string.
"""

DT_CTG_PROGRAM = "dt.ctg.program"
"""Name of the CICS program.
This attribute expects a value of type string.
"""

DT_CTG_COMMAREALENGTH = "dt.ctg.commarealength"
"""Length of the communication area.
This attribute expects a value of type int.
"""

DT_CTG_EXTENDMODE = "dt.ctg.extendmode"
"""See "ExtendModes" section below.
This attribute expects a value of type int.
"""

DT_CTG_TERMID = "dt.ctg.termid"
"""Name of the terminal resource.
This attribute expects a value of type string.
"""

DT_CTG_RC = "dt.ctg.rc"
"""CTG response code.
This attribute expects a value of type int.
"""

DT_DB_TOPOLOGY = "dt.db.topology"
"""The topology of the database in relation to the application performing database requests.
This attribute expects a value of type string from the enumeration DtDbTopologyValues.
"""

DT_DB_EXECUTION_TYPE = "dt.db.execution_type"
"""How a query is executed, as a query or update. Should not parse the query but should be determined by which method was called to execute the query. For example in JDBC terms it would be "executeQuery" -> query and all other "execute*" methods -> update.
This attribute expects a value of type string from the enumeration DtDbExecutionTypeValues.
"""

DT_EXCEPTION_TYPES = "dt.exception.types"
"""The exception types of a caused-by chain, represented by their fully-qualified type names encoded as a single string (see [Encoding of Exception Data](https://bitbucket.lab.dynatrace.org/projects/ODIN/repos/odin-spec/browse/spec/semantic_conventions/exception_conventions.md#encoding-of-exception-data)).
This attribute expects a value of type string.
"""

DT_EXCEPTION_MESSAGES = "dt.exception.messages"
"""Messages providing details about the exceptions of a caused-by chain encoded as a single string (see [Encoding of Exception Data](https://bitbucket.lab.dynatrace.org/projects/ODIN/repos/odin-spec/browse/spec/semantic_conventions/exception_conventions.md#encoding-of-exception-data)).
This attribute expects a value of type string.
"""

DT_EXCEPTION_SERIALIZED_STACKTRACES = "dt.exception.serialized_stacktraces"
"""Stack traces for all exceptions in a caused-by chain, serialized into a single string (see [Encoding of Exception Data](https://bitbucket.lab.dynatrace.org/projects/ODIN/repos/odin-spec/browse/spec/semantic_conventions/exception_conventions.md#encoding-of-exception-data)).
This attribute expects a value of type string.
"""

FAAS_TRIGGER = "faas.trigger"
"""Type of the trigger on which the function is executed.
This attribute expects a value of type string from the enumeration FaasTriggerValues.
"""

FAAS_EXECUTION = "faas.execution"
"""The execution ID of the current function execution.
This attribute expects a value of type string.
"""

DT_FAAS_AWS_X_AMZN_TRACE_ID = "dt.faas.aws.x_amzn_trace_id"
"""The `X-Amzn-Trace-Id` HTTP response header for [AWS X-Ray](https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html) tracing.
This attribute expects a value of type string.
"""

DT_FAAS_AWS_X_AMZN_REQUEST_ID = "dt.faas.aws.x_amzn_request_id"
"""The AWS `X-Amzn-RequestId` HTTP response header.
This attribute expects a value of type string.

Note: The different notation of the `RequestId` part (missing `-` character) compared to `X-Amzn-Trace-Id` is intentional.
"""

DT_CODE_FUNC = "dt.code.func"
"""The method or function name, or equivalent (usually rightmost part of the code unit's name).
This attribute expects a value of type string.

.. deprecated::
   Use `code.function` instead.
"""

DT_CODE_NS = "dt.code.ns"
"""The "namespace" within which `dt.code.func` is defined. Usually the qualified class or module name, such that `dt.code.ns` + some separator + `dt.code.func` form a unique identifier for the code unit.
This attribute expects a value of type string.

.. deprecated::
   Use `code.namespace` instead.
"""

DT_CODE_FILEPATH = "dt.code.filepath"
"""The source code file name that identifies the code unit as uniquely as possible (preferably an absolute file path).
This attribute expects a value of type string.

.. deprecated::
   Use `code.filepath` instead.
"""

DT_CODE_LINENO = "dt.code.lineno"
"""The line number in `dt.code.filepath` best representing the operation. It SHOULD point within the code unit named in `dt.code.func`.
This attribute expects a value of type int.

.. deprecated::
   Use `code.lineno` instead.
"""

DT_STACKTRACE_ONSTART = "dt.stacktrace.onstart"
"""Full stacktrace of call to Span.Start (possibly including call to span processor's OnStart).
This attribute expects a value of type string.
"""

DT_STACKTRACE_ONEND = "dt.stacktrace.onend"
"""Full stacktrace of call to Span.End (possibly including call to span processor's OnEnd).
This attribute expects a value of type string.
"""

HTTP_METHOD = "http.method"
"""HTTP request method.
This attribute expects a value of type string.
"""

HTTP_URL = "http.url"
"""Full HTTP request URL in the form `scheme://host[:port]/path?query[#fragment]`. Usually the fragment is not transmitted over HTTP, but if it is known, it should be included nevertheless.
This attribute expects a value of type string.
"""

HTTP_TARGET = "http.target"
"""The full request target as passed in a HTTP request line or equivalent.
This attribute expects a value of type string.
"""

HTTP_HOST = "http.host"
"""The value of the [HTTP host header](https://rfc-editor.org/rfc/rfc7230#section-5.4). When the header is empty or not present, this attribute should be the same.
This attribute expects a value of type string.
"""

HTTP_SCHEME = "http.scheme"
"""The URI scheme identifying the used protocol.
This attribute expects a value of type string.
"""

HTTP_STATUS_CODE = "http.status_code"
"""[HTTP response status code](https://rfc-editor.org/rfc/rfc7231#section-6).
This attribute expects a value of type int.
"""

HTTP_STATUS_TEXT = "http.status_text"
"""[HTTP reason phrase](https://rfc-editor.org/rfc/rfc7230#section-3.1.2).
This attribute expects a value of type string.
"""

HTTP_FLAVOR = "http.flavor"
"""Kind of HTTP protocol used.
This attribute expects a value of type string from the enumeration HttpFlavorValues.

Note: If `net.transport` is not specified, it can be assumed to be `IP.TCP` except if `http.flavor` is `QUIC`, in which case `IP.UDP` is assumed.
"""

HTTP_USER_AGENT = "http.user_agent"
"""Value of the [HTTP User-Agent](https://rfc-editor.org/rfc/rfc7231#section-5.5.3) header sent by the client.
This attribute expects a value of type string.
"""

HTTP_REQUEST_CONTENT_LENGTH = "http.request_content_length"
"""The size of the request payload body in bytes. This is the number of bytes transferred excluding headers and is often, but not always, present as the [Content-Length](https://rfc-editor.org/rfc/rfc7230#section-3.3.2) header. For requests using transport encoding, this should be the compressed size.
This attribute expects a value of type int.
"""

HTTP_REQUEST_CONTENT_LENGTH_UNCOMPRESSED = "http.request_content_length_uncompressed"
"""The size of the uncompressed request payload body after transport decoding. Not set if transport encoding not used.
This attribute expects a value of type int.
"""

HTTP_RESPONSE_CONTENT_LENGTH = "http.response_content_length"
"""The size of the response payload body in bytes. This is the number of bytes transferred excluding headers and is often, but not always, present as the [Content-Length](https://rfc-editor.org/rfc/rfc7230#section-3.3.2) header. For requests using transport encoding, this should be the compressed size.
This attribute expects a value of type int.
"""

HTTP_RESPONSE_CONTENT_LENGTH_UNCOMPRESSED = "http.response_content_length_uncompressed"
"""The size of the uncompressed response payload body after transport decoding. Not set if transport encoding not used.
This attribute expects a value of type int.
"""

NET_HOST_IP = "net.host.ip"
"""Like `net.peer.ip` but for the host IP. Useful in case of a multi-IP host.
This attribute expects a value of type string.
"""

NET_HOST_PORT = "net.host.port"
"""Like `net.peer.port` but for the host port.
This attribute expects a value of type int.
"""

NET_HOST_NAME = "net.host.name"
"""Local hostname or similar, see note below.
This attribute expects a value of type string.
"""

HTTP_SERVER_NAME = "http.server_name"
"""The primary server name of the matched virtual host. This should be obtained via configuration. If no such configuration can be obtained, this attribute MUST NOT be set ( `net.host.name` should be used instead).
This attribute expects a value of type string.

Note: http.url is usually not readily available on the server side but would have to be assembled in a cumbersome and sometimes lossy process from other information (see e.g. open-telemetry/opentelemetry-python/pull/148). It is thus preferred to supply the raw data that is available.
"""

HTTP_ROUTE = "http.route"
"""The matched route (path template).
This attribute expects a value of type string.
"""

HTTP_CLIENT_IP = "http.client_ip"
"""The IP address of the original client behind all proxies, if known (e.g. from [X-Forwarded-For](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For)).
This attribute expects a value of type string.

Note: This is not necessarily the same as `net.peer.ip`, which would identify the network-level peer, which may be a proxy.
"""

DT_HTTP_APPLICATION_ID = "dt.http.application_id"
"""Tech-dependent, eg. servlet context.
This attribute expects a value of type string.
"""

DT_HTTP_CONTEXT_ROOT = "dt.http.context_root"
"""The path prefix of the URL that identifies this HTTP application. If multiple roots exist, the one that was matched for this request should be used.
This attribute expects a value of type string.

Note: See [OTel definition](https://github.com/open-telemetry/opentelemetry-specification/blob/v0.6.0/specification/trace/semantic_conventions/http.md#http-server-definitions).
"""

DT_HTTP_REQUEST_HEADER_REFERER = "dt.http.request.header.referer"
"""`Referer` header.
This attribute expects a value of type string.
"""

DT_HTTP_REQUEST_HEADER_X_DYNATRACE_TEST = "dt.http.request.header.x-dynatrace-test"
"""`X-Dynatrace-Test` header.
This attribute expects a value of type string.
"""

DT_HTTP_REQUEST_HEADER_X_DYNATRACE_TENANT = "dt.http.request.header.x-dynatrace-tenant"
"""`X-Dynatrace-Tenant` header.
This attribute expects a value of type string.
"""

DT_HTTP_REQUEST_HEADER_FORWARDED = "dt.http.request.header.forwarded"
"""`Forwarded` header.
This attribute expects a value of type string.
"""

DT_HTTP_REQUEST_HEADER_X_FORWARDED_FOR = "dt.http.request.header.x-forwarded-for"
"""`X-Forwarded-For` header (only required if `dt.http.request.header.forwarded` isn't provided).
This attribute expects a value of type string.
"""

DT_IMS_IS_IMS = "dt.ims.is_ims"
"""Set to true for an interaction with IMS SOAP Gateway.
This attribute expects a value of type boolean.

Note: This value is normally either unset or `true`.
"""

OTEL_LIBRARY_NAME = "otel.library.name"
"""Contains the instrumentation library name.
This attribute expects a value of type string.
"""

OTEL_LIBRARY_VERSION = "otel.library.version"
"""Contains the instrumentation library version.
This attribute expects a value of type string.
"""

MESSAGING_SYSTEM = "messaging.system"
"""A string identifying the messaging system.
This attribute expects a value of type string.
"""

MESSAGING_DESTINATION = "messaging.destination"
"""The message destination name. This might be equal to the span name but is required nevertheless.
This attribute expects a value of type string.
"""

MESSAGING_DESTINATION_KIND = "messaging.destination_kind"
"""The kind of message destination.
This attribute expects a value of type string from the enumeration MessagingDestinationKindValues.
"""

MESSAGING_TEMP_DESTINATION = "messaging.temp_destination"
"""A boolean that is true if the message destination is temporary.
This attribute expects a value of type boolean.
"""

MESSAGING_PROTOCOL = "messaging.protocol"
"""The name of the transport protocol.
This attribute expects a value of type string.
"""

MESSAGING_PROTOCOL_VERSION = "messaging.protocol_version"
"""The version of the transport protocol.
This attribute expects a value of type string.
"""

MESSAGING_URL = "messaging.url"
"""Connection string.
This attribute expects a value of type string.
"""

MESSAGING_MESSAGE_ID = "messaging.message_id"
"""A value used by the messaging system as an identifier for the message, represented as a string.
This attribute expects a value of type string.
"""

MESSAGING_CONVERSATION_ID = "messaging.conversation_id"
"""A value identifying the conversation to which the message belongs, represented as a string. Sometimes called "Correlation ID".
This attribute expects a value of type string.
"""

MESSAGING_MESSAGE_PAYLOAD_SIZE_BYTES = "messaging.message_payload_size_bytes"
"""The (uncompressed) size of the message payload in bytes. Also use this attribute if it is unknown whether the compressed or uncompressed payload size is reported.
This attribute expects a value of type int.
"""

MESSAGING_MESSAGE_PAYLOAD_COMPRESSED_SIZE_BYTES = "messaging.message_payload_compressed_size_bytes"
"""The compressed size of the message payload in bytes.
This attribute expects a value of type int.
"""

DT_MESSAGING_IBM_QUEUEMANAGER_NAME = "dt.messaging.ibm.queuemanager.name"
"""Name of IBM's queue manager.
This attribute expects a value of type string.

Note: Only for IBM MQ spans.
"""

DT_MESSAGING_JMS_MESSAGE_TYPE = "dt.messaging.jms.message_type"
"""The type of content of the jms message.
This attribute expects a value of type string from the enumeration DtMessagingJmsMessageTypeValues.
"""

DT_MESSAGING_BATCH_SIZE = "dt.messaging.batch_size"
"""Number of messages being sent/received/processed at once.
This attribute expects a value of type int.

Note: This batch size attribute is kind of a workaround for situations where we cannot better distinguish the individual messages.
"""

DT_PARENT_IS_SUPPRESSED_PRIMARY = "dt.parent.is_suppressed_primary"
"""MUST be set to `true` if this is a link that would have been the parent but was suppressed by the OpenTelemetry integration.
This attribute expects a value of type boolean.
"""

DT_RUM_DTC = "dt.rum.dtc"
"""Value of x-dtc header.
This attribute expects a value of type string.
"""

DT_RUM_APP_ME_ID = "dt.rum.app_me_id"
"""Monitored entity id of configured application.
This attribute expects a value of type string.
"""

DT_RUM_CLIENTIP_HEADER_NAME = "dt.rum.clientip_header_name"
"""Name of the header in `dt.http.request.headers` to parse clientip from.
This attribute expects a value of type string.
"""

DT_ZOSCONNECT_PROGRAM = "dt.zosconnect.program"
"""The name of the z/OS application program called by the request.
This attribute expects a value of type string.
"""

DT_ZOSCONNECT_REQUEST_ID = "dt.zosconnect.request_id"
"""The z/OS Connect request ID.
This attribute expects a value of type int.
"""

DT_ZOSCONNECT_SERVICE_PROVIDER_NAME = "dt.zosconnect.service_provider_name"
"""The service provider name.
This attribute expects a value of type string.
"""

DT_ZOSCONNECT_SOR_REFERENCE = "dt.zosconnect.sor_reference"
"""The system of record reference.
This attribute expects a value of type string.
"""

DT_ZOSCONNECT_SOR_IDENTIFIER = "dt.zosconnect.sor_identifier"
"""The system of record identifier.  The format differs depending on the SOR type.
This attribute expects a value of type string.

Note: <https://www.ibm.com/support/knowledgecenter/SS4SVW_3.0.0/javadoc/com/ibm/zosconnect/spi/Data.html?view=embed#SOR_IDENTIFIER>.
"""

DT_ZOSCONNECT_SOR_RESOURCE = "dt.zosconnect.sor_resource"
"""Identifier for the resource invoked on the system of record. The format differs depending on the SOR type.
This attribute expects a value of type string.

Note: <https://www.ibm.com/support/knowledgecenter/SS4SVW_3.0.0/javadoc/com/ibm/zosconnect/spi/Data.html?view=embed#SOR_RESOURCE>.
"""

DT_ZOSCONNECT_SOR_TYPE = "dt.zosconnect.sor_type"
"""The system of record type.
This attribute expects a value of type string from the enumeration DtZosconnectSorTypeValues.
"""

DT_ZOSCONNECT_INPUT_PAYLOAD_LENGTH = "dt.zosconnect.input_payload_length"
"""The length of the request payload in bytes.
This attribute expects a value of type int.
"""

DT_ZOSCONNECT_OUTPUT_PAYLOAD_LENGTH = "dt.zosconnect.output_payload_length"
"""The length of the response payload in bytes.
This attribute expects a value of type int.
"""

DT_ZOSCONNECT_API_NAME = "dt.zosconnect.api_name"
"""The z/OS Connect API name.
This attribute expects a value of type string.
"""

DT_ZOSCONNECT_SERVICE_NAME = "dt.zosconnect.service_name"
"""The z/OS Connect service name.
This attribute expects a value of type string.
"""

DT_ZOSCONNECT_API_DESCRIPTION = "dt.zosconnect.api_description"
"""The z/OS Connect API description.
This attribute expects a value of type string.
"""

DT_ZOSCONNECT_SERVICE_DESCRIPTION = "dt.zosconnect.service_description"
"""The z/OS Connect service description.
This attribute expects a value of type string.
"""

DT_ZOSCONNECT_API_VERSION = "dt.zosconnect.api_version"
"""The z/OS Connect API version.
This attribute expects a value of type string.
"""

DT_ZOSCONNECT_SERVICE_VERSION = "dt.zosconnect.service_version"
"""The z/OS Connect service version.
This attribute expects a value of type string.
"""

DT_ZOSCONNECT_REQUEST_TYPE = "dt.zosconnect.request_type"
"""The type of the REST request.
This attribute expects a value of type string from the enumeration DtZosconnectRequestTypeValues.

Note: <https://www.ibm.com/support/knowledgecenter/SS4SVW_3.0.0/javadoc/com/ibm/zosconnect/spi/Data.RequestType.html>.
"""

FAAS_DOCUMENT_COLLECTION = "faas.document.collection"
"""The name of the source on which the triggering operation was performed. For example, in Cloud Storage or S3 corresponds to the bucket name, and in Cosmos DB to the database name.
This attribute expects a value of type string.
"""

FAAS_DOCUMENT_OPERATION = "faas.document.operation"
"""Describes the type of the operation that was performed on the data.
This attribute expects a value of type string from the enumeration FaasDocumentOperationValues.
"""

FAAS_DOCUMENT_TIME = "faas.document.time"
"""A string containing the time when the data was accessed in the [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) format expressed in [UTC](https://www.w3.org/TR/NOTE-datetime).
This attribute expects a value of type string.
"""

FAAS_DOCUMENT_NAME = "faas.document.name"
"""The document name/table subjected to the operation. For example, in Cloud Storage or S3 is the name of the file, and in Cosmos DB the table name.
This attribute expects a value of type string.
"""

FAAS_TIME = "faas.time"
"""A string containing the function invocation time in the [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) format expressed in [UTC](https://www.w3.org/TR/NOTE-datetime).
This attribute expects a value of type string.
"""

FAAS_CRON = "faas.cron"
"""A string containing the schedule period as [Cron Expression](https://docs.oracle.com/cd/E12058_01/doc/doc.1014/e12030/cron_expressions.htm).
This attribute expects a value of type string.
"""

FAAS_COLDSTART = "faas.coldstart"
"""A boolean that is true if the serverless function is executed for the first time (aka cold-start).
This attribute expects a value of type boolean.
"""

FAAS_INVOKED_NAME = "faas.invoked_name"
"""The name of the invoked function.
This attribute expects a value of type string.

Note: SHOULD be equal to the `faas.name` resource attribute of the invoked function.
"""

FAAS_INVOKED_PROVIDER = "faas.invoked_provider"
"""The cloud provider of the invoked function.
This attribute expects a value of type string from the enumeration FaasInvokedProviderValues.

Note: SHOULD be equal to the `cloud.provider` resource attribute of the invoked function.
"""

FAAS_INVOKED_REGION = "faas.invoked_region"
"""The cloud region of the invoked function.
This attribute expects a value of type string.

Note: SHOULD be equal to the `cloud.region` resource attribute of the invoked function.
"""

ENDUSER_ID = "enduser.id"
"""Username or client_id extracted from the access token or Authorization header in the inbound request from outside the system.
This attribute expects a value of type string.
"""

ENDUSER_ROLE = "enduser.role"
"""Actual/assumed role the client is making the request under extracted from token or application security context.
This attribute expects a value of type string.
"""

ENDUSER_SCOPE = "enduser.scope"
"""Scopes or granted authorities the client currently possesses extracted from token or application security context. The value would come from the scope associated with an OAuth 2.0 Access Token or an attribute value in a SAML 2.0 Assertion.
This attribute expects a value of type string.
"""

RPC_SYSTEM = "rpc.system"
"""The value `aws-api`.
This attribute expects a value of type string from the enumeration RpcSystemValues.
"""

RPC_SERVICE = "rpc.service"
"""The name of the service to which a request is made, as returned by the AWS SDK.
This attribute expects a value of type string.

Note: This is the logical name of the service from the RPC interface perspective, which can be different from the name of any implementing class. The `code.namespace` attribute may be used to store the latter (despite the attribute name, it may include a class name; e.g., class with method actually executing the call on the server side, RPC client stub class on the client side).
"""

RPC_METHOD = "rpc.method"
"""The name of the operation corresponding to the request, as returned by the AWS SDK.
This attribute expects a value of type string.

Note: This is the logical name of the method from the RPC interface perspective, which can be different from the name of any implementing method/function. The `code.function` attribute may be used to store the latter (e.g., method actually executing the call on the server side, RPC client stub method on the client side).
"""

AWS_DYNAMODB_TABLE_NAMES = "aws.dynamodb.table_names"
"""The keys in the `RequestItems` object field.
This attribute expects a value of type string[].
"""

AWS_DYNAMODB_CONSUMED_CAPACITY = "aws.dynamodb.consumed_capacity"
"""The JSON-serialized value of each item in the `ConsumedCapacity` response field.
This attribute expects a value of type string[].
"""

AWS_DYNAMODB_ITEM_COLLECTION_METRICS = "aws.dynamodb.item_collection_metrics"
"""The JSON-serialized value of the `ItemCollectionMetrics` response field.
This attribute expects a value of type string.
"""

AWS_DYNAMODB_PROVISIONED_READ_CAPACITY = "aws.dynamodb.provisioned_read_capacity"
"""The value of the `ProvisionedThroughput.ReadCapacityUnits` request parameter.
This attribute expects a value of type double.
"""

AWS_DYNAMODB_PROVISIONED_WRITE_CAPACITY = "aws.dynamodb.provisioned_write_capacity"
"""The value of the `ProvisionedThroughput.WriteCapacityUnits` request parameter.
This attribute expects a value of type double.
"""

AWS_DYNAMODB_CONSISTENT_READ = "aws.dynamodb.consistent_read"
"""The value of the `ConsistentRead` request parameter.
This attribute expects a value of type boolean.
"""

AWS_DYNAMODB_PROJECTION = "aws.dynamodb.projection"
"""The value of the `ProjectionExpression` request parameter.
This attribute expects a value of type string.
"""

AWS_DYNAMODB_LIMIT = "aws.dynamodb.limit"
"""The value of the `Limit` request parameter.
This attribute expects a value of type int.
"""

AWS_DYNAMODB_ATTRIBUTES_TO_GET = "aws.dynamodb.attributes_to_get"
"""The value of the `AttributesToGet` request parameter.
This attribute expects a value of type string[].
"""

AWS_DYNAMODB_INDEX_NAME = "aws.dynamodb.index_name"
"""The value of the `IndexName` request parameter.
This attribute expects a value of type string.
"""

AWS_DYNAMODB_SELECT = "aws.dynamodb.select"
"""The value of the `Select` request parameter.
This attribute expects a value of type string.
"""

AWS_DYNAMODB_GLOBAL_SECONDARY_INDEXES = "aws.dynamodb.global_secondary_indexes"
"""The JSON-serialized value of each item of the `GlobalSecondaryIndexes` request field.
This attribute expects a value of type string[].
"""

AWS_DYNAMODB_LOCAL_SECONDARY_INDEXES = "aws.dynamodb.local_secondary_indexes"
"""The JSON-serialized value of each item of the `LocalSecondaryIndexes` request field.
This attribute expects a value of type string[].
"""

AWS_DYNAMODB_EXCLUSIVE_START_TABLE = "aws.dynamodb.exclusive_start_table"
"""The value of the `ExclusiveStartTableName` request parameter.
This attribute expects a value of type string.
"""

AWS_DYNAMODB_TABLE_COUNT = "aws.dynamodb.table_count"
"""The the number of items in the `TableNames` response parameter.
This attribute expects a value of type int.
"""

AWS_DYNAMODB_SCAN_FORWARD = "aws.dynamodb.scan_forward"
"""The value of the `ScanIndexForward` request parameter.
This attribute expects a value of type boolean.
"""

AWS_DYNAMODB_SEGMENT = "aws.dynamodb.segment"
"""The value of the `Segment` request parameter.
This attribute expects a value of type int.
"""

AWS_DYNAMODB_TOTAL_SEGMENTS = "aws.dynamodb.total_segments"
"""The value of the `TotalSegments` request parameter.
This attribute expects a value of type int.
"""

AWS_DYNAMODB_COUNT = "aws.dynamodb.count"
"""The value of the `Count` response parameter.
This attribute expects a value of type int.
"""

AWS_DYNAMODB_SCANNED_COUNT = "aws.dynamodb.scanned_count"
"""The value of the `ScannedCount` response parameter.
This attribute expects a value of type int.
"""

AWS_DYNAMODB_ATTRIBUTE_DEFINITIONS = "aws.dynamodb.attribute_definitions"
"""The JSON-serialized value of each item in the `AttributeDefinitions` request field.
This attribute expects a value of type string[].
"""

AWS_DYNAMODB_GLOBAL_SECONDARY_INDEX_UPDATES = "aws.dynamodb.global_secondary_index_updates"
"""The JSON-serialized value of each item in the the `GlobalSecondaryIndexUpdates` request field.
This attribute expects a value of type string[].
"""

AWS_REGION = "aws.region"
"""The cloud region of the invoked resource.
This attribute expects a value of type string.

Note: SHOULD be equal to the `cloud.region` resource attribute of the invoked resource.
"""

MESSAGING_OPERATION = "messaging.operation"
"""A string identifying which part and kind of message consumption this span describes.
This attribute expects a value of type string from the enumeration MessagingOperationValues.
"""

RPC_GRPC_STATUS_CODE = "rpc.grpc.status_code"
"""The [numeric status code](https://github.com/grpc/grpc/blob/v1.33.2/doc/statuscodes.md) of the gRPC request.
This attribute expects a value of type int from the enumeration RpcGrpcStatusCodeValues.
"""

RPC_JSONRPC_VERSION = "rpc.jsonrpc.version"
"""Protocol version as in `jsonrpc` property of request/response. Since JSON-RPC 1.0 does not specify this, the value can be omitted.
This attribute expects a value of type string.
"""

RPC_JSONRPC_REQUEST_ID = "rpc.jsonrpc.request_id"
"""`id` property of request or response. Since protocol allows id to be int, string, `null` or missing (for notifications), value is expected to be cast to string for simplicity. Use empty string in case of `null` value. Omit entirely if this is a notification.
This attribute expects a value of type string.
"""

RPC_JSONRPC_ERROR_CODE = "rpc.jsonrpc.error_code"
"""`error.code` property of response if it is an error response.
This attribute expects a value of type int.
"""

RPC_JSONRPC_ERROR_MESSAGE = "rpc.jsonrpc.error_message"
"""`error.message` property of response if it is an error response.
This attribute expects a value of type string.
"""

MESSAGE_TYPE = "message.type"
"""Whether this is a received or sent message.
This attribute expects a value of type string from the enumeration MessageTypeValues.
"""

MESSAGE_ID = "message.id"
"""MUST be calculated as two different counters starting from `1` one for sent messages and one for received message.
This attribute expects a value of type int.

Note: This way we guarantee that the values will be consistent between different implementations.
"""

MESSAGE_COMPRESSED_SIZE = "message.compressed_size"
"""Compressed size of the message in bytes.
This attribute expects a value of type int.
"""

MESSAGE_UNCOMPRESSED_SIZE = "message.uncompressed_size"
"""Uncompressed size of the message in bytes.
This attribute expects a value of type int.
"""


# Enum definitions
class CloudProviderValues(Enum):
   AWS = "aws"
   AZURE = "azure"
   GCP = "gcp"


class CloudPlatformValues(Enum):
   AWS_EC2 = "aws_ec2"
   AWS_ECS = "aws_ecs"
   AWS_EKS = "aws_eks"
   AWS_LAMBDA = "aws_lambda"
   AWS_ELASTIC_BEANSTALK = "aws_elastic_beanstalk"
   AZURE_VM = "azure_vm"
   AZURE_CONTAINER_INSTANCES = "azure_container_instances"
   AZURE_AKS = "azure_aks"
   AZURE_FUNCTIONS = "azure_functions"
   AZURE_APP_SERVICE = "azure_app_service"
   GCP_COMPUTE_ENGINE = "gcp_compute_engine"
   GCP_CLOUD_RUN = "gcp_cloud_run"
   GCP_KUBERNETES_ENGINE = "gcp_kubernetes_engine"
   GCP_CLOUD_FUNCTIONS = "gcp_cloud_functions"
   GCP_APP_ENGINE = "gcp_app_engine"


class DtFaasAwsInitializationTypeValues(Enum):
   ON_DEMAND = "on-demand"
   PROVISIONED_CONCURRENCY = "provisioned-concurrency"
   SNAP_START = "snap-start"


class DtOsTypeValues(Enum):
   UNKNOWN = "UNKNOWN"
   WINDOWS = "WINDOWS"
   LINUX = "LINUX"
   HPUX = "HPUX"
   AIX = "AIX"
   SOLARIS = "SOLARIS"
   ZOS = "ZOS"
   DARWIN = "DARWIN"


class DtTechAgentDetectedMainTechnologyValues(Enum):
   UNKNOWN = "unknown"
   AWS_LAMBDA = "aws_lambda"
   ZOS_CONNECT = "zos_connect"
   CTG = "ctg"
   IMS = "ims"
   WEBSPHERE_AS = "websphere_as"
   WEBSPHERE_LIBERTY = "websphere_liberty"


class TelemetryExporterNameValues(Enum):
   ODIN = "odin"


class HostArchValues(Enum):
   AMD64 = "amd64"
   ARM32 = "arm32"
   ARM64 = "arm64"
   IA64 = "ia64"
   PPC32 = "ppc32"
   PPC64 = "ppc64"
   S390X = "s390x"
   X86 = "x86"


class ProcessRuntimeNameValues(Enum):
   BEAM = "BEAM"
   GC = "Go compiler"
   GCCGO = "GCC Go frontend"
   NODEJS = "NodeJS"
   BROWSER = "Web Browser"
   IOJS = "io.js"
   DOTNET_CORE = ".NET Core, .NET 5+"
   DOTNET_FRAMEWORK = ".NET Framework"
   MONO = "Mono"
   CPYTHON = "CPython"
   IRONPYTHON = "IronPython"
   JYTHON = "Jython"
   PYPY = "PyPy"
   PYTHONNET = "PythonNet"


class TelemetrySdkLanguageValues(Enum):
   CPP = "cpp"
   DOTNET = "dotnet"
   ERLANG = "erlang"
   GO = "go"
   JAVA = "java"
   NODEJS = "nodejs"
   PHP = "php"
   PYTHON = "python"
   RUBY = "ruby"
   WEBJS = "webjs"


class DbSystemValues(Enum):
   OTHER_SQL = "other_sql"
   MSSQL = "mssql"
   MYSQL = "mysql"
   ORACLE = "oracle"
   DB2 = "db2"
   POSTGRESQL = "postgresql"
   REDSHIFT = "redshift"
   HIVE = "hive"
   CLOUDSCAPE = "cloudscape"
   HSQLSB = "hsqlsb"
   PROGRESS = "progress"
   MAXDB = "maxdb"
   HANADB = "hanadb"
   INGRES = "ingres"
   FIRSTSQL = "firstsql"
   EDB = "edb"
   CACHE = "cache"
   ADABAS = "adabas"
   FIREBIRD = "firebird"
   DERBY = "derby"
   FILEMAKER = "filemaker"
   INFORMIX = "informix"
   INSTANTDB = "instantdb"
   INTERBASE = "interbase"
   MARIADB = "mariadb"
   NETEZZA = "netezza"
   PERVASIVE = "pervasive"
   POINTBASE = "pointbase"
   SQLITE = "sqlite"
   SYBASE = "sybase"
   TERADATA = "teradata"
   VERTICA = "vertica"
   H2 = "h2"
   COLDFUSION = "coldfusion"
   CASSANDRA = "cassandra"
   HBASE = "hbase"
   MONGODB = "mongodb"
   REDIS = "redis"
   COUCHBASE = "couchbase"
   COUCHDB = "couchdb"
   COSMOSDB = "cosmosdb"
   DYNAMODB = "dynamodb"
   NEO4J = "neo4j"


class NetTransportValues(Enum):
   IP_TCP = "IP.TCP"
   IP_UDP = "IP.UDP"
   IP = "IP"
   UNIX = "Unix"
   PIPE = "pipe"
   INPROC = "inproc"
   OTHER = "other"


class DtCtgRequesttypeValues(Enum):
   BASE = "BASE"
   ECI = "ECI"
   EPI = "EPI"
   ESI = "ESI"
   XA = "XA"
   ADMIN = "ADMIN"
   AUTH = "AUTH"


class DtCtgCalltypeValues(Enum):
   ECI_UNKNOWN_CALL_TYPE = 0
   ECI_SYNC = 1
   ECI_ASYNC = 2
   ECI_GET_REPLY = 3
   ECI_GET_REPLY_WAIT = 4
   ECI_GET_SPECIFIC_REPLY = 5
   ECI_GET_SPECIFIC_REPLY_WAIT = 6
   ECI_STATE_SYNC = 7
   ECI_STATE_ASYNC = 8
   CICS_ECI_LIST_SYSTEMS = 9
   ECI_STATE_SYNC_JAVA = 10
   ECI_STATE_ASYNC_JAVA = 11
   ECI_SYNC_TPN = 12
   ECI_ASYNC_TPN = 13


class DtDbTopologyValues(Enum):
   NOT_SET = "not_set"
   SINGLE_SERVER = "single_server"
   EMBEDDED = "embedded"
   FAILOVER = "failover"
   LOAD_BALANCING = "load_balancing"
   LOCAL_IPC = "local_ipc"
   CLUSTER = "cluster"


class DtDbExecutionTypeValues(Enum):
   UPDATE = "update"
   QUERY = "query"


class FaasTriggerValues(Enum):
   DATASOURCE = "datasource"
   HTTP = "http"
   PUBSUB = "pubsub"
   TIMER = "timer"
   OTHER = "other"


class HttpFlavorValues(Enum):
   HTTP_1_0 = "1.0"
   HTTP_1_1 = "1.1"
   HTTP_2_0 = "2.0"
   SPDY = "SPDY"
   QUIC = "QUIC"


class MessagingDestinationKindValues(Enum):
   QUEUE = "queue"
   TOPIC = "topic"


class DtMessagingJmsMessageTypeValues(Enum):
   OTHER = "other"
   MAP = "map"
   OBJECT = "object"
   STREAM = "stream"
   BYTES = "bytes"
   TEXT = "text"


class DtZosconnectSorTypeValues(Enum):
   CICS = "CICS"
   IMS = "IMS"
   REST = "REST"
   WOLA = "WOLA"
   MQ = "MQ"


class DtZosconnectRequestTypeValues(Enum):
   API = "API"
   SERVICE = "SERVICE"
   ADMIN = "ADMIN"
   UNKNOWN = "UNKNOWN"


class FaasDocumentOperationValues(Enum):
   INSERT = "insert"
   EDIT = "edit"
   DELETE = "delete"


class FaasInvokedProviderValues(Enum):
   AWS = "aws"
   AZURE = "azure"
   GCP = "gcp"


class RpcSystemValues(Enum):
   GRPC = "grpc"
   JAVA_RMI = "java_rmi"
   DOTNET_WCF = "dotnet_wcf"
   APACHE_DUBBO = "apache_dubbo"


class MessagingOperationValues(Enum):
   RECEIVE = "receive"
   PROCESS = "process"


class RpcGrpcStatusCodeValues(Enum):
   OK = 0
   CANCELLED = 1
   UNKNOWN = 2
   INVALID_ARGUMENT = 3
   DEADLINE_EXCEEDED = 4
   NOT_FOUND = 5
   ALREADY_EXISTS = 6
   PERMISSION_DENIED = 7
   RESOURCE_EXHAUSTED = 8
   FAILED_PRECONDITION = 9
   ABORTED = 10
   OUT_OF_RANGE = 11
   UNIMPLEMENTED = 12
   INTERNAL = 13
   UNAVAILABLE = 14
   DATA_LOSS = 15
   UNAUTHENTICATED = 16


class MessageTypeValues(Enum):
   SENT = "SENT"
   RECEIVED = "RECEIVED"

