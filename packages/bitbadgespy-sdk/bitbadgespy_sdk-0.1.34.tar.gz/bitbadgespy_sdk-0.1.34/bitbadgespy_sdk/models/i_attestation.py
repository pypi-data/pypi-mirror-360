# coding: utf-8

"""
    BitBadges API

    # Introduction The BitBadges API is a RESTful API that enables developers to interact with the BitBadges blockchain and indexer. This API provides comprehensive access to the BitBadges ecosystem, allowing you to query and interact with digital badges, collections, accounts, blockchain data, and more. For complete documentation, see the [BitBadges Documentation](https://docs.bitbadges.io/for-developers/bitbadges-api/api) and use along with this reference.  Note: The API + documentation is new and may contain bugs. If you find any issues, please let us know via Discord or another contact method (https://bitbadges.io/contact).  # Getting Started  ## Authentication All API requests require an API key for authentication. You can obtain your API key from the [BitBadges Developer Portal](https://bitbadges.io/developer).  ### API Key Authentication Include your API key in the `x-api-key` header: ``` x-api-key: your-api-key-here ```  <br />  ## User Authentication Most read-only applications can function with just an API key. However, if you need to access private user data or perform actions on behalf of users, you have two options:  ### OAuth 2.0 (Sign In with BitBadges) For performing actions on behalf of other users, use the standard OAuth 2.0 flow via Sign In with BitBadges. See the [Sign In with BitBadges documentation](https://docs.bitbadges.io/for-developers/authenticating-with-bitbadges) for details.  You will pass the access token in the Authorization header: ``` Authorization: Bearer your-access-token-here ```  ### Password Self-Approve Method For automating actions for your own account: 1. Set up an approved password sign in in your account settings tab on https://bitbadges.io with desired scopes (e.g. `completeClaims`) 2. Sign in using: ```typescript const { message } = await BitBadgesApi.getSignInChallenge(...); const verificationRes = await BitBadgesApi.verifySignIn({     message,     signature: '', //Empty string     password: '...' }) ```  Note: This method uses HTTP session cookies. Ensure your requests support credentials (e.g. axios: { withCredentials: true }).  ### Scopes Note that for proper authentication, you must have the proper scopes set.  See [https://bitbadges.io/auth/linkgen](https://bitbadges.io/auth/linkgen) for a helper URL generation tool. The scopes will be included in the `scope` parameter of the SIWBB URL or set in your approved sign in settings.  Note that stuff marked as Full Access is typically reserved for the official site. If you think you may need this, contact us.  ### Available Scopes  - **Report** (`report`)   Report users or collections.  - **Read Profile** (`readProfile`)   Read your private profile information. This includes your email, approved sign-in methods, connections, and other private information.  - **Read Address Lists** (`readAddressLists`)   Read private address lists on behalf of the user.  - **Manage Address Lists** (`manageAddressLists`)   Create, update, and delete address lists on behalf of the user (private or public).  - **Manage Applications** (`manageApplications`)   Create, update, and delete applications on behalf of the user.  - **Manage Claims** (`manageClaims`)   Create, update, and delete claims on behalf of the user.  - **Manage Developer Apps** (`manageDeveloperApps`)   Create, update, and delete developer apps on behalf of the user.  - **Manage Dynamic Stores** (`manageDynamicStores`)   Create, update, and delete dynamic stores on behalf of the user.  - **Manage Utility Listings** (`manageUtilityListings`)   Create, update, and delete utility listings on behalf of the user.  - **Approve Sign In With BitBadges Requests** (`approveSignInWithBitBadgesRequests`)   Sign In with BitBadges on behalf of the user.  - **Read Authentication Codes** (`readAuthenticationCodes`)   Read Authentication Codes on behalf of the user.  - **Delete Authentication Codes** (`deleteAuthenticationCodes`)   Delete Authentication Codes on behalf of the user.  - **Send Claim Alerts** (`sendClaimAlerts`)   Send claim alerts on behalf of the user.  - **Read Claim Alerts** (`readClaimAlerts`)   Read claim alerts on behalf of the user. Note that claim alerts may contain sensitive information like claim codes, attestation IDs, etc.  - **Manage Attestations** (`manageAttestations`)   Manage attestations on behalf of the user. This includes creating, updating, and deleting attestations.  - **Read Attestations** (`readAttestations`)   Read attestations on behalf of the user.  - **Read Private Claim Data** (`readPrivateClaimData`)   Read private claim data on behalf of the user (e.g. codes, passwords, private user lists, etc.).  - **Complete Claims** (`completeClaims`)   Complete claims on behalf of the user.  - **Manage Off-Chain Balances** (`manageOffChainBalances`)   Manage off-chain balances on behalf of the user.  - **Embedded Wallet** (`embeddedWallet`)   Sign transactions on behalf of the user with their embedded wallet.  <br />  ## SDK Integration The recommended way to interact with the API is through our TypeScript/JavaScript SDK:  ```typescript import { BigIntify, BitBadgesAPI } from \"bitbadgesjs-sdk\";  // Initialize the API client const api = new BitBadgesAPI({   convertFunction: BigIntify,   apiKey: 'your-api-key-here' });  // Example: Fetch collections const collections = await api.getCollections({   collectionsToFetch: [{     collectionId: 1n,     metadataToFetch: {       badgeIds: [{ start: 1n, end: 10n }]     }   }] }); ```  <br />  # Tiers There are 3 tiers of API keys, each with different rate limits and permissions. See the pricing page for more details: https://bitbadges.io/pricing - Free tier - Premium tier - Enterprise tier  Rate limit headers included in responses: - `X-RateLimit-Limit`: Total requests allowed per window - `X-RateLimit-Remaining`: Remaining requests in current window - `X-RateLimit-Reset`: Time until rate limit resets (UTC timestamp)  # Response Formats  ## Error Response  All API errors follow a consistent format:  ```typescript {   // Serialized error object for debugging purposes   // Advanced users can use this to debug issues   error?: any;    // UX-friendly error message that can be displayed to the user   // Always present if error occurs   errorMessage: string;    // Authentication error flag   // Present if the user is not authenticated   unauthorized?: boolean; } ```  <br />  ## Pagination Cursor-based pagination is used for list endpoints: ```typescript {   items: T[],   bookmark: string, // Use this for the next page   hasMore: boolean } ```  <br />  # Best Practices 1. **Rate Limiting**: Implement proper rate limit handling 2. **Caching**: Cache responses when appropriate 3. **Error Handling**: Handle API errors gracefully 4. **Batch Operations**: Use batch endpoints when possible  # Additional Resources - [Official Documentation](https://docs.bitbadges.io/for-developers/bitbadges-api/api) - [SDK Documentation](https://docs.bitbadges.io/for-developers/bitbadges-sdk/overview) - [Developer Portal](https://bitbadges.io/developer) - [GitHub SDK Repository](https://github.com/bitbadges/bitbadgesjs) - [Quickstarter Repository](https://github.com/bitbadges/bitbadges-quickstart)  # Support - [Contact Page](https://bitbadges.io/contact)

    The version of the OpenAPI document: 0.1
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from bitbadgespy_sdk.models.i_attestation_anchors_inner import IAttestationAnchorsInner
from bitbadgespy_sdk.models.i_attestation_data_integrity_proof import IAttestationDataIntegrityProof
from bitbadgespy_sdk.models.i_attestation_proof_of_issuance import IAttestationProofOfIssuance
from bitbadgespy_sdk.models.number_type import NumberType
from typing import Optional, Set
from typing_extensions import Self

class IAttestation(BaseModel):
    """
    IAttestation
    """ # noqa: E501
    message_format: StrictStr = Field(description="The message format of the messages.", alias="messageFormat")
    created_by: StrictStr = Field(description="All supported addresses map to a Bech32 BitBadges address which is used by the BitBadges blockchain behind the scenes. For conversion, see the BitBadges documentation. If this type is used, we must always convert to a BitBadges address before using it.", alias="createdBy")
    created_at: NumberType = Field(description="Numeric timestamp - value is equal to the milliseconds since the UNIX epoch.", alias="createdAt")
    entropies: List[StrictStr] = Field(description="Entropies used for certain data integrity proofs on-chain (e.g. HASH(message + entropy) = on-chain value)")
    public_visibility: Optional[StrictBool] = Field(default=None, description="Whether or not the attestation is displayable on the user's profile. if true, the attestation can be queried by anyone with the ID.", alias="publicVisibility")
    proof_of_issuance: Optional[IAttestationProofOfIssuance] = Field(default=None, alias="proofOfIssuance")
    attestation_id: StrictStr = Field(description="The attestation ID. This is the constant ID that is given to the attestation.", alias="attestationId")
    invite_code: StrictStr = Field(description="The inviteCode is used to add the attestation to the user's wallet. Anyone with the key can query it, so keep this safe and secure.", alias="inviteCode")
    scheme: StrictStr = Field(description="The scheme of the attestation. BBS+ signatures are supported and can be used where selective disclosure is a requirement. Otherwise, you can simply use your native blockchain's signature scheme.")
    original_provider: Optional[StrictStr] = Field(default=None, description="The original provider of the attestation. Used for third-party attestation providers.", alias="originalProvider")
    messages: List[StrictStr] = Field(description="Thesse are the attestations that are signed. For BBS+ signatures, there can be >1 messages, and the signer can selectively disclose the attestations. For standard signatures, there is only 1 attestationMessage.")
    data_integrity_proof: Optional[IAttestationDataIntegrityProof] = Field(default=None, alias="dataIntegrityProof")
    name: StrictStr = Field(description="Metadata for the attestation for display purposes. Note this should not contain anything sensitive. It may be displayed to verifiers.")
    image: StrictStr = Field(description="Metadata for the attestation for display purposes. Note this should not contain anything sensitive. It may be displayed to verifiers.")
    description: StrictStr = Field(description="Metadata for the attestation for display purposes. Note this should not contain anything sensitive. It may be displayed to verifiers.")
    holders: List[StrictStr] = Field(description="Holders are the addresses that have been given the attestation.")
    all_holders: Optional[List[StrictStr]] = Field(default=None, description="All holders are the addresses that have been given the attestation at any point in time. Used internally as an append-only audit log.", alias="allHolders")
    anchors: List[IAttestationAnchorsInner] = Field(description="Anchors are on-chain transactions used to prove certain things about the attestation. For example, you can anchor the attestation to a transaction hash to prove that the attestation existed at a certain time.")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["messageFormat", "createdBy", "createdAt", "entropies", "publicVisibility", "proofOfIssuance", "attestationId", "inviteCode", "scheme", "originalProvider", "messages", "dataIntegrityProof", "name", "image", "description", "holders", "allHolders", "anchors"]

    @field_validator('message_format')
    def message_format_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['plaintext', 'json']):
            raise ValueError("must be one of enum values ('plaintext', 'json')")
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of IAttestation from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * Fields in `self.additional_properties` are added to the output dict.
        """
        excluded_fields: Set[str] = set([
            "additional_properties",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of created_at
        if self.created_at:
            _dict['createdAt'] = self.created_at.to_dict()
        # override the default output from pydantic by calling `to_dict()` of proof_of_issuance
        if self.proof_of_issuance:
            _dict['proofOfIssuance'] = self.proof_of_issuance.to_dict()
        # override the default output from pydantic by calling `to_dict()` of data_integrity_proof
        if self.data_integrity_proof:
            _dict['dataIntegrityProof'] = self.data_integrity_proof.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in anchors (list)
        _items = []
        if self.anchors:
            for _item_anchors in self.anchors:
                if _item_anchors:
                    _items.append(_item_anchors.to_dict())
            _dict['anchors'] = _items
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of IAttestation from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "messageFormat": obj.get("messageFormat"),
            "createdBy": obj.get("createdBy"),
            "createdAt": NumberType.from_dict(obj["createdAt"]) if obj.get("createdAt") is not None else None,
            "entropies": obj.get("entropies"),
            "publicVisibility": obj.get("publicVisibility"),
            "proofOfIssuance": IAttestationProofOfIssuance.from_dict(obj["proofOfIssuance"]) if obj.get("proofOfIssuance") is not None else None,
            "attestationId": obj.get("attestationId"),
            "inviteCode": obj.get("inviteCode"),
            "scheme": obj.get("scheme"),
            "originalProvider": obj.get("originalProvider"),
            "messages": obj.get("messages"),
            "dataIntegrityProof": IAttestationDataIntegrityProof.from_dict(obj["dataIntegrityProof"]) if obj.get("dataIntegrityProof") is not None else None,
            "name": obj.get("name"),
            "image": obj.get("image"),
            "description": obj.get("description"),
            "holders": obj.get("holders"),
            "allHolders": obj.get("allHolders"),
            "anchors": [IAttestationAnchorsInner.from_dict(_item) for _item in obj["anchors"]] if obj.get("anchors") is not None else None
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


