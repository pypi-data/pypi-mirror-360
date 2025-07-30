#
# # Copyright © 2025 Peak AI Limited. or its affiliates. All Rights Reserved.
# #
# # Licensed under the Apache License, Version 2.0 (the "License"). You
# # may not use this file except in compliance with the License. A copy of
# # the License is located at:
# #
# # https://github.com/PeakBI/peak-sdk/blob/main/LICENSE
# #
# # or in the "license" file accompanying this file. This file is
# # distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# # ANY KIND, either express or implied. See the License for the specific
# # language governing permissions and limitations under the License.
# #
# # This file is part of the peak-sdk.
# # see (https://github.com/PeakBI/peak-sdk)
# #
# # You should have received a copy of the APACHE LICENSE, VERSION 2.0
# # along with this program. If not, see <https://apache.org/licenses/LICENSE-2.0>
#
"""Contains the metadata for all the commands.

The metadata represents the following:
    - table_params: Parameters required for the table output formatting.
    - request_body_yaml_path: File containing the yaml file examples for the command.
"""

from __future__ import annotations

from typing import Any, Dict, List


def tag_parser(data: Any) -> str:
    tag_array = [tag["name"] for tag in data]
    return ", ".join(tag_array)


command_metadata: Dict[str, Any] = {
    "images>list": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "name": {
                    "label": "Image Name",
                },
                "type": {
                    "label": "Type",
                },
                "scope": {
                    "label": "Scope",
                },
                "latestVersion.id": {
                    "label": "Latest Version ID",
                },
                "latestVersion.version": {
                    "label": "Latest Version",
                },
                "latestVersion.status": {
                    "label": "Latest Version Status",
                },
                "latestVersion.lastBuildStatus": {
                    "label": "Latest Version Build Status",
                },
                "latestVersion.tags": {
                    "label": "Tags",
                    "parser": tag_parser,
                },
            },
            "title": "Images",
            "data_key": "images",
            "subheader_key": "imageCount",
        },
    },
    "images>list-versions": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "version": {
                    "label": "Version",
                },
                "description": {
                    "label": "Description",
                },
                "status": {
                    "label": "Status",
                },
                "lastBuildStatus": {
                    "label": "Last Build Status",
                },
                "buildDetails": {
                    "label": "Build Details",
                },
                "tags": {
                    "label": "Tags",
                    "parser": tag_parser,
                },
            },
            "title": "Image Versions",
            "data_key": "versions",
            "subheader_key": "versionCount",
        },
    },
    "images>list-builds": {
        "table_params": {
            "output_keys": {
                "buildId": {
                    "label": "Build ID",
                },
                "versionId": {
                    "label": "Version ID",
                },
                "version": {
                    "label": "Version",
                },
                "status": {
                    "label": "Build Status",
                },
                "startedAt": {
                    "label": "Started At (UTC)",
                },
                "finishedAt": {
                    "label": "Finished At (UTC)",
                },
            },
            "title": "Image Builds",
            "data_key": "builds",
            "subheader_key": "buildCount",
        },
    },
    "workflows>list": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "name": {
                    "label": "Workflow Name",
                },
                "status": {
                    "label": "Status",
                },
                "triggers": {
                    "label": "Triggers",
                },
                "lastExecution.status": {
                    "label": "Last Execution Status",
                },
                "lastExecution.executedAt": {
                    "label": "Last Execution Time (UTC)",
                },
                "tags": {
                    "label": "Tags",
                    "parser": tag_parser,
                },
            },
            "title": "Workflows",
            "data_key": "workflows",
            "subheader_key": "workflowsCount",
        },
    },
    "workflows>list-executions": {
        "table_params": {
            "output_keys": {
                "executionId": {
                    "label": "Execution ID",
                },
                "status": {
                    "label": "Status",
                },
                "duration": {
                    "label": "Run Duration",
                },
                "executedAt": {
                    "label": "Execution Time (UTC)",
                },
            },
            "title": "Workflows Executions",
            "data_key": "executions",
            "subheader_key": "executionsCount",
        },
    },
    "workflows>get-execution-details": {
        "table_params": {
            "output_keys": {
                "name": {
                    "label": "Step Name",
                },
                "startedAt": {
                    "label": "Started At",
                },
                "finishedAt": {
                    "label": "Finished At",
                },
                "status": {
                    "label": "Status",
                },
                "stepType": {
                    "label": "Step Type",
                },
                "image": {
                    "label": "Image",
                },
                "output": {
                    "label": "Output",
                },
            },
            "title": "Execution Details",
            "data_key": "steps",
            "subheader_title": "Execution Status",
            "subheader_key": "status",
        },
    },
    "webapps>list": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "name": {
                    "label": "Name",
                },
                "status": {
                    "label": "Status",
                },
                "updatedBy": {
                    "label": "Updated By",
                },
                "updatedAt": {
                    "label": "Updated At (UTC)",
                },
                "tags": {
                    "label": "Tags",
                    "parser": tag_parser,
                },
            },
            "title": "Webapps",
            "data_key": "webapps",
            "subheader_key": "webappsCount",
        },
    },
    "services>list": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "name": {
                    "label": "Name",
                },
                "serviceType": {
                    "label": "Service Type",
                },
                "status": {
                    "label": "Status",
                },
                "updatedBy": {
                    "label": "Updated By",
                },
                "updatedAt": {
                    "label": "Updated At (UTC)",
                },
                "tags": {
                    "label": "Tags",
                    "parser": tag_parser,
                },
            },
            "title": "Services",
            "data_key": "services",
            "subheader_key": "servicesCount",
        },
    },
    "artifacts>list": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "description": {
                    "label": "Description",
                },
                "name": {
                    "label": "Name",
                },
                "createdAt": {
                    "label": "Created At (UTC)",
                },
                "createdBy": {
                    "label": "Created By",
                },
            },
            "title": "Artifacts",
            "data_key": "artifacts",
            "subheader_key": "artifactCount",
        },
    },
    "specs>list": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "kind": {
                    "label": "Kind",
                },
                "metadata.name": {
                    "label": "Name",
                },
                "metadata.status": {
                    "label": "Status",
                },
                "latestRelease.version": {
                    "label": "Latest Release",
                },
                "metadata.tags": {
                    "label": "Tags",
                    "parser": tag_parser,
                },
            },
            "title": "Specs",
            "data_key": "specs",
            "subheader_key": "specCount",
        },
    },
    "specs>list-release-deployments": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "kind": {
                    "label": "Kind",
                },
                "metadata.name": {
                    "label": "Name",
                },
                "metadata.status": {
                    "label": "Status",
                },
                "latestRevision.revision": {
                    "label": "Latest Revision",
                },
                "latestRevision.status": {
                    "label": "Latest Revision Status",
                },
                "metadata.tags": {
                    "label": "Tags",
                    "parser": tag_parser,
                },
            },
            "title": "Deployments for a Spec Release",
            "data_key": "deployments",
            "subheader_key": "deploymentCount",
        },
    },
    "deployments>list": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "kind": {
                    "label": "Kind",
                },
                "metadata.title": {
                    "label": "Title",
                },
                "metadata.status": {
                    "label": "Status",
                },
                "latestRevision.revision": {
                    "label": "Latest Revision",
                },
                "latestRevision.status": {
                    "label": "Latest Revision Status",
                },
                "metadata.tags": {
                    "label": "Tags",
                    "parser": tag_parser,
                },
            },
            "title": "Deployments",
            "data_key": "deployments",
            "subheader_key": "deploymentCount",
        },
    },
    "apps>specs>list": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "kind": {
                    "label": "Kind",
                },
                "metadata.name": {
                    "label": "Name",
                },
                "metadata.status": {
                    "label": "Status",
                },
                "latestRelease.version": {
                    "label": "Latest Release",
                },
                "metadata.tags": {
                    "label": "Tags",
                    "parser": tag_parser,
                },
            },
            "title": "Specs",
            "data_key": "specs",
            "subheader_key": "specCount",
        },
    },
    "apps>specs>list-releases": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "version": {
                    "label": "Version",
                },
                "notes": {
                    "label": "Notes",
                },
                "createdAt": {
                    "label": "Created At (UTC)",
                },
                "createdBy": {
                    "label": "Created By",
                },
            },
            "title": "Spec Releases",
            "data_key": "releases",
            "subheader_key": "releaseCount",
        },
    },
    "apps>deployments>list": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "kind": {
                    "label": "Kind",
                },
                "metadata.title": {
                    "label": "Title",
                },
                "metadata.status": {
                    "label": "Status",
                },
                "latestRevision.revision": {
                    "label": "Latest Revision",
                },
                "latestRevision.status": {
                    "label": "Latest Revision Status",
                },
                "metadata.tags": {
                    "label": "Tags",
                    "parser": tag_parser,
                },
            },
            "title": "App Deployments",
            "data_key": "deployments",
            "subheader_key": "deploymentCount",
        },
    },
    "apps>deployments>list-revisions": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "notes": {
                    "label": "Notes",
                },
                "revision": {
                    "label": "Revision",
                },
                "status": {
                    "label": "Status",
                },
            },
            "title": "App Deployment Revisions",
            "data_key": "revisions",
            "subheader_key": "revisionCount",
        },
    },
    "blocks>specs>list": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "kind": {
                    "label": "Kind",
                },
                "metadata.name": {
                    "label": "Name",
                },
                "metadata.status": {
                    "label": "Status",
                },
                "latestRelease.version": {
                    "label": "Latest Release",
                },
                "metadata.tags": {
                    "label": "Tags",
                    "parser": tag_parser,
                },
            },
            "title": "Block Specs",
            "data_key": "specs",
            "subheader_key": "specCount",
        },
    },
    "blocks>specs>list-releases": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "version": {
                    "label": "Version",
                },
                "notes": {
                    "label": "Notes",
                },
                "createdAt": {
                    "label": "Created At (UTC)",
                },
                "createdBy": {
                    "label": "Created By",
                },
            },
            "title": "Block Spec Releases",
            "data_key": "releases",
            "subheader_key": "releaseCount",
        },
    },
    "blocks>deployments>list": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "kind": {
                    "label": "Kind",
                },
                "metadata.title": {
                    "label": "Title",
                },
                "metadata.status": {
                    "label": "Status",
                },
                "latestRevision.revision": {
                    "label": "Latest Revision",
                },
                "latestRevision.status": {
                    "label": "Latest Revision Status",
                },
                "metadata.tags": {
                    "label": "Tags",
                    "parser": tag_parser,
                },
            },
            "title": "Block Deployments",
            "data_key": "deployments",
            "subheader_key": "deploymentCount",
        },
    },
    "blocks>deployments>list-revisions": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "notes": {
                    "label": "Notes",
                },
                "revision": {
                    "label": "Revision",
                },
                "status": {
                    "label": "Status",
                },
            },
            "title": "Block Deployment Revisions",
            "data_key": "revisions",
            "subheader_key": "revisionCount",
        },
    },
    "deployments>execute-resources": {
        "table_params": {
            "output_keys": {
                "blockSpecId": {
                    "label": "Block Spec ID",
                },
                "version": {
                    "label": "Version",
                },
                "executionId": {
                    "label": "Execution ID",
                },
                "status": {
                    "label": "Execution Status",
                },
            },
            "title": "Trigger Resources",
            "data_key": "executeResponse",
        },
    },
    "tenants>list-instance-options": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "name": {
                    "label": "Instance Name",
                },
                "cpu": {
                    "label": "CPU",
                },
                "memory": {
                    "label": "Memory",
                },
                "gpu": {
                    "label": "GPU",
                },
                "gpuMemory": {
                    "label": "GPU Memory",
                },
                "provider": {
                    "label": "Provider",
                },
            },
            "title": "Instance Options",
            "data_key": "data",
        },
    },
    "alerts>emails>list": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "subject": {
                    "label": "Subject",
                },
                "status": {
                    "label": "Status",
                },
                "templateName": {
                    "label": "Template Name",
                },
                "createdAt": {
                    "label": "Created At",
                },
                "createdBy": {
                    "label": "Created By",
                },
            },
            "title": "Emails",
            "data_key": "emails",
            "subheader_key": "emailCount",
        },
    },
    "alerts>emails>list-templates": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "name": {
                    "label": "Name",
                },
                "scope": {
                    "label": "Status",
                },
                "createdAt": {
                    "label": "Created At",
                },
                "createdBy": {
                    "label": "Created By",
                },
            },
            "title": "Templates",
            "data_key": "templates",
            "subheader_key": "templateCount",
        },
    },
    "metrics>list": {
        "table_params": {
            "output_keys": {
                "name": {
                    "label": "Name",
                },
                "type": {
                    "label": "Type",
                },
                "description": {
                    "label": "Description",
                },
                "collectionId": {
                    "label": "Collection ID",
                },
                "publicationId": {
                    "label": "Publication ID",
                },
                "metadata": {
                    "label": "Metadata",
                },
            },
            "title": "Metrics",
            "data_key": "data",
            "subheader_key": "totalCount",
        },
    },
    "metrics>list>measure": {
        "table_params": {
            "output_keys": {
                "name": {
                    "label": "Name",
                },
                "type": {
                    "label": "Type",
                },
                "aggType": {
                    "label": "Aggregation Type",
                },
                "cube": {
                    "label": "Cube",
                },
                "description": {
                    "label": "Description",
                },
                "collectionId": {
                    "label": "Collection ID",
                },
                "publicationId": {
                    "label": "Publication ID",
                },
                "metadata": {
                    "label": "Metadata",
                },
            },
            "title": "Measures",
            "data_key": "data",
            "subheader_key": "totalCount",
        },
    },
    "metrics>list>dimension": {
        "table_params": {
            "output_keys": {
                "name": {
                    "label": "Name",
                },
                "type": {
                    "label": "Type",
                },
                "primaryKey": {
                    "label": "Primary Key",
                },
                "cube": {
                    "label": "Cube",
                },
                "description": {
                    "label": "Description",
                },
                "collectionId": {
                    "label": "Collection ID",
                },
                "publicationId": {
                    "label": "Publication ID",
                },
                "metadata": {
                    "label": "Metadata",
                },
            },
            "title": "Dimensions",
            "data_key": "data",
            "subheader_key": "totalCount",
        },
    },
    "metrics>list>segment": {
        "table_params": {
            "output_keys": {
                "name": {
                    "label": "Name",
                },
                "cube": {
                    "label": "Cube",
                },
                "description": {
                    "label": "Description",
                },
                "collectionId": {
                    "label": "Collection ID",
                },
                "publicationId": {
                    "label": "Publication ID",
                },
                "metadata": {
                    "label": "Metadata",
                },
            },
            "title": "Segments",
            "data_key": "data",
            "subheader_key": "totalCount",
        },
    },
    "metrics>list-collections": {
        "table_params": {
            "output_keys": {
                "id": {
                    "label": "ID",
                },
                "name": {
                    "label": "Name",
                },
                "description": {
                    "label": "Description",
                },
                "scope": {
                    "label": "Scope",
                },
                "createdAt": {
                    "label": "Created At",
                },
                "createdBy": {
                    "label": "Created By",
                },
            },
            "title": "Collections",
            "data_key": "collections",
            "subheader_key": "totalCount",
        },
    },
    "metrics>list-namespaces": {
        "table_params": {
            "output_keys": {
                "name": {
                    "label": "Name",
                },
                "models": {
                    "label": "Models",
                },
            },
            "title": "Namespaces",
            "data_key": "namespaces",
            "subheader_key": "totalCount",
        },
    },
    "artifacts>create": {
        "request_body_yaml_path": "sample_yaml/resources/artifacts/create_artifact.yaml",
    },
    "artifacts>update-metadata": {
        "request_body_yaml_path": "sample_yaml/resources/artifacts/update_artifact_metadata.yaml",
    },
    "artifacts>create-version": {
        "request_body_yaml_path": "sample_yaml/resources/artifacts/create_artifact_version.yaml",
    },
    "images>create": {
        "request_body_yaml_path": "sample_yaml/resources/images/upload/create_image.yaml",
    },
    "images>create-version": {
        "request_body_yaml_path": "sample_yaml/resources/images/upload/create_image_version.yaml",
    },
    "images>update-version": {
        "request_body_yaml_path": "sample_yaml/resources/images/upload/update_version.yaml",
    },
    "images>create-or-update": {
        "request_body_yaml_path": "sample_yaml/resources/images/upload/create_or_update_image.yaml",
    },
    "workflows>create": {
        "request_body_yaml_path": "sample_yaml/resources/workflows/create_workflow.yaml",
    },
    "workflows>update": {
        "request_body_yaml_path": "sample_yaml/resources/workflows/update_workflow.yaml",
    },
    "workflows>create-or-update": {
        "request_body_yaml_path": "sample_yaml/resources/workflows/create_or_update_workflow.yaml",
    },
    "workflows>patch": {
        "request_body_yaml_path": "sample_yaml/resources/workflows/patch_workflow.yaml",
    },
    "workflows>execute": {
        "request_body_yaml_path": "sample_yaml/resources/workflows/execute_workflow.yaml",
    },
    "webapps>create": {
        "request_body_yaml_path": "sample_yaml/resources/webapps/create_webapp.yaml",
    },
    "webapps>update": {
        "request_body_yaml_path": "sample_yaml/resources/webapps/update_webapp.yaml",
    },
    "webapps>create-or-update": {
        "request_body_yaml_path": "sample_yaml/resources/webapps/create_or_update_webapp.yaml",
    },
    "services>create": {
        "request_body_yaml_path": "sample_yaml/resources/services/create_service.yaml",
    },
    "services>update": {
        "request_body_yaml_path": "sample_yaml/resources/services/update_service.yaml",
    },
    "services>create-or-update": {
        "request_body_yaml_path": "sample_yaml/resources/services/create_or_update_service.yaml",
    },
    "services>test": {
        "request_body_yaml_path": "sample_yaml/resources/services/test_service.yaml",
    },
    "alerts>emails>send": {
        "request_body_yaml_path": "sample_yaml/resources/emails/send_email.yaml",
    },
    "apps>specs>create": {
        "request_body_yaml_path": "sample_yaml/press/apps/specs/create_app_spec.yaml",
    },
    "apps>specs>update-metadata": {
        "request_body_yaml_path": "sample_yaml/press/apps/specs/update_app_spec_metadata.yaml",
    },
    "apps>specs>create-release": {
        "request_body_yaml_path": "sample_yaml/press/apps/specs/create_app_spec_release.yaml",
    },
    "apps>deployments>create": {
        "request_body_yaml_path": "sample_yaml/press/apps/deployments/create_app_deployment.yaml",
    },
    "apps>deployments>create-revision": {
        "request_body_yaml_path": "sample_yaml/press/apps/deployments/create_app_deployment_revision.yaml",
    },
    "apps>deployments>update-metadata": {
        "request_body_yaml_path": "sample_yaml/press/apps/deployments/update_app_deployment_metadata.yaml",
    },
    "blocks>specs>create": {
        "request_body_yaml_path": "sample_yaml/press/blocks/specs/workflow/create_block_spec.yaml",
    },
    "blocks>specs>update-metadata": {
        "request_body_yaml_path": "sample_yaml/press/blocks/specs/update_block_spec_metadata.yaml",
    },
    "blocks>specs>create-release": {
        "request_body_yaml_path": "sample_yaml/press/blocks/specs/workflow/create_block_spec_release.yaml",
    },
    "blocks>deployments>create": {
        "request_body_yaml_path": "sample_yaml/press/blocks/deployments/create_block_deployment.yaml",
    },
    "blocks>deployments>create-revision": {
        "request_body_yaml_path": "sample_yaml/press/blocks/deployments/create_block_deployment_revision.yaml",
    },
    "blocks>deployments>update-metadata": {
        "request_body_yaml_path": "sample_yaml/press/blocks/deployments/update_block_deployment_metadata.yaml",
    },
    "blocks>deployments>patch-parameters": {
        "request_body_yaml_path": "sample_yaml/press/blocks/deployments/patch_block_parameters.yaml",
    },
    "deployments>patch-parameters": {
        "request_body_yaml_path": "sample_yaml/press/patch_parameters.yaml",
    },
    "deployments>patch-parameters-v2": {
        "request_body_yaml_path": "sample_yaml/press/deployments/patch_app_parameters_v2.yaml",
    },
    "metrics>publish": {
        "request_body_yaml_path": "sample_yaml/metrics/publish.yaml",
    },
    "metrics>query": {
        "request_body_yaml_path": "sample_yaml/metrics/query.yaml",
        "table_params": {
            "output_keys": {},
            "title": "Query Data",
            "data_key": "data",
            "subheader_key": "totalCount",
        },
    },
    "metrics>create-collection": {
        "request_body_yaml_path": "sample_yaml/metrics/create_collection.yaml",
    },
}

command_parameter: Dict[str, str] = {
    "metrics>list": "type",
}

__all__: List[str] = ["command_metadata", "command_parameter"]
