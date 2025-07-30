from dataclasses import dataclass
from typing import Union

from simba_sdk.core.requests.client.credential import schemas as credential_schemas


@dataclass
class AdminListVcsQuery:
    page: int
    size: int
    id__in: Union[str, None] = None
    order_by: Union[str, None] = None
    metadata__or__fields: Union[str, None] = None
    metadata__owner: Union[str, None] = None
    metadata__holder: Union[str, None] = None
    metadata__owner_alias: Union[str, None] = None
    metadata__issuer_name__ilike: Union[str, None] = None
    metadata__holder_alias: Union[str, None] = None
    metadata__subject_name__ilike: Union[str, None] = None
    metadata__tags__in: Union[str, None] = None
    metadata__status__in: Union[str, None] = None
    metadata__created_at__lte: Union[str, None] = None
    metadata__created_at__gte: Union[str, None] = None
    metadata__updated_at__lte: Union[str, None] = None
    metadata__updated_at__gte: Union[str, None] = None
    vc__id: Union[str, None] = None
    vc__issuer: Union[str, None] = None
    vc__type__in: Union[str, None] = None
    vc__validFrom__lte: Union[str, None] = None
    vc__validFrom__gte: Union[str, None] = None
    vc__validUntil__lte: Union[str, None] = None
    vc__validUntil__gte: Union[str, None] = None
    credentialSubject__id: Union[str, None] = None
    credentialSubject__claim__fields: Union[str, None] = None


@dataclass
class AdminListVpsQuery:
    page: int
    size: int
    metadata__created_at__lte: Union[str, None] = None
    metadata__created_at__gte: Union[str, None] = None
    metadata__updated_at__lte: Union[str, None] = None
    metadata__updated_at__gte: Union[str, None] = None
    metadata__owner: Union[str, None] = None
    vp__type__in: Union[str, None] = None
    vp__validFrom__lte: Union[str, None] = None
    vp__validFrom__gte: Union[str, None] = None
    vp__validUntil__lte: Union[str, None] = None
    vp__validUntil__gte: Union[str, None] = None
    verifiableCredential__id: Union[str, None] = None
    verifiableCredential__issuer: Union[str, None] = None
    verifiableCredential__type__in: Union[str, None] = None
    verifiableCredential__validFrom__lte: Union[str, None] = None
    verifiableCredential__validFrom__gte: Union[str, None] = None
    verifiableCredential__validUntil__lte: Union[str, None] = None
    verifiableCredential__validUntil__gte: Union[str, None] = None
    credentialSubject__id: Union[str, None] = None
    credentialSubject__claim__fields: Union[str, None] = None


@dataclass
class AdminListTasksQuery:
    page: int
    size: int
    id: Union[str, None] = None
    owner: Union[str, None] = None
    order_by: Union[str, None] = None
    status__in: Union[str, None] = None
    type__in: Union[str, None] = None
    created_at__lte: Union[str, None] = None
    created_at__gte: Union[str, None] = None
    updated_at__lte: Union[str, None] = None
    updated_at__gte: Union[str, None] = None


@dataclass
class ListDidStringsQuery:
    page: int
    size: int
    order_by: Union[str, None] = None
    include_hidden: Union[bool, None] = None
    did_document__id: Union[str, None] = None
    did_document__id__like: Union[str, None] = None
    did_document__id__startswith: Union[str, None] = None
    metadata__domain: Union[str, None] = None


@dataclass
class GetDidDocumentQuery:
    force_resolve: Union[bool, None] = None


@dataclass
class ListCustodialAccountsQuery:
    domain: str
    page: int
    size: int
    trust_profile: Union[str, None] = None


@dataclass
class GetPublicVcQuery:
    vc_id: str


@dataclass
class ListTrustProfilesQuery:
    page: int
    size: int
    id: Union[str, None] = None
    created_at__lte: Union[str, None] = None
    created_at__gte: Union[str, None] = None
    updated_at__lte: Union[str, None] = None
    updated_at__gte: Union[str, None] = None
    name: Union[str, None] = None
    name__ilike: Union[str, None] = None
    did_method: Union[str, None] = None
    cryptosuite: Union[str, None] = None
    blockchain: Union[str, None] = None
    registry_type: Union[str, None] = None
    contract_api: Union[str, None] = None
    order_by: Union[str, None] = None


@dataclass
class ListDidsQuery:
    page: int
    size: int
    include_stats: Union[bool, None] = None
    output_format: Union[credential_schemas.DIDResponseType, None] = None
    simba_id: Union[str, None] = None
    order_by: Union[str, None] = None
    include_hidden: Union[bool, None] = None
    metadata__search: Union[str, None] = None
    metadata__name__ilike: Union[str, None] = None
    metadata__permission: Union[credential_schemas.DidPermission, None] = None
    metadata__alias__ilike: Union[str, None] = None
    metadata__tags__in: Union[str, None] = None
    metadata__status__in: Union[str, None] = None
    metadata__created_at__lte: Union[str, None] = None
    metadata__created_at__gte: Union[str, None] = None
    metadata__updated_at__lte: Union[str, None] = None
    metadata__updated_at__gte: Union[str, None] = None
    did_document__id: Union[str, None] = None
    did_document__id__like: Union[str, None] = None
    did_document__id__startswith: Union[str, None] = None
    did_document__controller: Union[str, None] = None


@dataclass
class ListPublicVcsQuery:
    page: int
    size: int
    id__in: Union[str, None] = None
    order_by: Union[str, None] = None
    metadata__owner_alias: Union[str, None] = None
    metadata__issuer_name__ilike: Union[str, None] = None
    metadata__holder_alias: Union[str, None] = None
    metadata__subject_name__ilike: Union[str, None] = None
    metadata__tags__in: Union[str, None] = None
    metadata__status__in: Union[str, None] = None
    metadata__created_at__lte: Union[str, None] = None
    metadata__created_at__gte: Union[str, None] = None
    metadata__updated_at__lte: Union[str, None] = None
    metadata__updated_at__gte: Union[str, None] = None
    vc__id: Union[str, None] = None
    vc__issuer: Union[str, None] = None
    vc__type__in: Union[str, None] = None
    vc__validFrom__lte: Union[str, None] = None
    vc__validFrom__gte: Union[str, None] = None
    vc__validUntil__lte: Union[str, None] = None
    vc__validUntil__gte: Union[str, None] = None
    credentialSubject__id: Union[str, None] = None
    credentialSubject__claim__fields: Union[str, None] = None


@dataclass
class ListVcsQuery:
    page: int
    size: int
    my_vcs: Union[bool, None] = None
    issued_vcs: Union[bool, None] = None
    id__in: Union[str, None] = None
    order_by: Union[str, None] = None
    metadata__owner_alias: Union[str, None] = None
    metadata__issuer_name__ilike: Union[str, None] = None
    metadata__holder_alias: Union[str, None] = None
    metadata__subject_name__ilike: Union[str, None] = None
    metadata__tags__in: Union[str, None] = None
    metadata__status__in: Union[str, None] = None
    metadata__created_at__lte: Union[str, None] = None
    metadata__created_at__gte: Union[str, None] = None
    metadata__updated_at__lte: Union[str, None] = None
    metadata__updated_at__gte: Union[str, None] = None
    vc__id: Union[str, None] = None
    vc__issuer: Union[str, None] = None
    vc__type__in: Union[str, None] = None
    vc__validFrom__lte: Union[str, None] = None
    vc__validFrom__gte: Union[str, None] = None
    vc__validUntil__lte: Union[str, None] = None
    vc__validUntil__gte: Union[str, None] = None
    credentialSubject__id: Union[str, None] = None
    credentialSubject__claim__fields: Union[str, None] = None


@dataclass
class AcceptVcQuery:
    accept: bool


@dataclass
class GetVpsQuery:
    page: int
    size: int
    id: Union[str, None] = None
    metadata__created_at__lte: Union[str, None] = None
    metadata__created_at__gte: Union[str, None] = None
    metadata__updated_at__lte: Union[str, None] = None
    metadata__updated_at__gte: Union[str, None] = None
    vp__type__in: Union[str, None] = None
    vp__validFrom__lte: Union[str, None] = None
    vp__validFrom__gte: Union[str, None] = None
    vp__validUntil__lte: Union[str, None] = None
    vp__validUntil__gte: Union[str, None] = None
    verifiableCredential__id: Union[str, None] = None
    verifiableCredential__issuer: Union[str, None] = None
    verifiableCredential__type__in: Union[str, None] = None
    verifiableCredential__validFrom__lte: Union[str, None] = None
    verifiableCredential__validFrom__gte: Union[str, None] = None
    verifiableCredential__validUntil__lte: Union[str, None] = None
    verifiableCredential__validUntil__gte: Union[str, None] = None
    credentialSubject__id: Union[str, None] = None
    credentialSubject__claim__fields: Union[str, None] = None


@dataclass
class ListTasksQuery:
    page: int
    size: int
    id: Union[str, None] = None
    order_by: Union[str, None] = None
    status__in: Union[str, None] = None
    type__in: Union[str, None] = None
    created_at__lte: Union[str, None] = None
    created_at__gte: Union[str, None] = None
    updated_at__lte: Union[str, None] = None
    updated_at__gte: Union[str, None] = None
