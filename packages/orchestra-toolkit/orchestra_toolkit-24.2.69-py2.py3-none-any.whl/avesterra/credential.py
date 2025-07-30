""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from avesterra.avesterra import AvEntity, AvMask, AvAuthorization, AuthorizationError
from avesterra.avial import AvKey, entity_key, AvValue, NULL_ENTITY
from avesterra.compartments import compartment_valid
from avesterra.identities import identity_valid
import avesterra.facts as facts
from avesterra.taxonomy import AvAttribute
import avesterra.compartments as compartments
import avesterra.identities as identities
import avesterra.features as features
import avesterra.tokens as tokens

# Avial 4.12 Added credential module, which issues or retracts credentials
# for an identity in a compartment.


def issue_credential(
    compartment: AvEntity,
    identity: AvEntity,
    mask: AvMask,
    authorization: AvAuthorization,
):
    compartment_key: AvKey = entity_key(entity=compartment, authorization=authorization)
    identity_key: AvKey = entity_key(entity=identity, authorization=authorization)

    if compartment_valid(
        compartment=compartment, authorization=authorization
    ) and identity_valid(identity=identity, authorization=authorization):
        facts.include_fact(
            entity=compartment,
            attribute=AvAttribute.CREDENTIAL,
            authorization=authorization,
        )

        compartment_authority: AvAuthorization = compartments.compartment_authority(
            compartment=compartment, authorization=authorization
        )
        identity_authority: AvAuthorization = identities.identity_authority(
            identity=identity, authorization=authorization
        )

        features.include_feature(
            entity=compartment,
            attribute=AvAttribute.CREDENTIAL,
            name=f"{mask}",
            key=identity_key,
            value=AvValue.encode_entity(identity),
            authorization=authorization,
        )
        features.include_feature(
            entity=identity,
            attribute=AvAttribute.CREDENTIAL,
            name=f"{mask}",
            key=compartment_key,
            value=AvValue.encode_entity(compartment),
            authorization=authorization,
        )
        tokens.map(
            server=NULL_ENTITY,
            token=identity_authority,
            mask=mask,
            authority=compartment_authority,
            authorization=authorization,
        )
    else:
        if not compartment_valid(compartment=compartment, authorization=authorization):
            raise ValueError(
                f"Invalid compartment {compartment} given for credential issuance"
            )
        if not identity_valid(identity=identity, authorization=authorization):
            raise ValueError(
                f"Invalid identity {identity} given for credential issuance"
            )


def retract_credential(
    compartment: AvEntity, identity: AvEntity, authorization: AvAuthorization
):
    compartment_key: AvKey = entity_key(entity=compartment, authorization=authorization)
    identity_key: AvKey = entity_key(entity=identity, authorization=authorization)

    if compartment_valid(
        compartment=compartment, authorization=authorization
    ) and identity_valid(identity=identity, authorization=authorization):
        facts.include_fact(
            entity=compartment,
            attribute=AvAttribute.CREDENTIAL,
            authorization=authorization,
        )

        compartment_authority: AvAuthorization = compartments.compartment_authority(
            compartment=compartment, authorization=authorization
        )
        identity_authority: AvAuthorization = identities.identity_authority(
            identity=identity, authorization=authorization
        )

        features.exclude_feature(
            entity=compartment,
            attribute=AvAttribute.CREDENTIAL,
            key=identity_key,
            authorization=authorization,
        )
        features.exclude_feature(
            entity=identity,
            attribute=AvAttribute.CREDENTIAL,
            key=compartment_key,
            authorization=authorization,
        )
        tokens.unmap(
            server=NULL_ENTITY,
            token=identity_authority,
            authority=compartment_authority,
            authorization=authorization,
        )
    else:
        if not compartment_valid(compartment=compartment, authorization=authorization):
            raise ValueError(
                f"Invalid compartment {compartment} given for credential retraction"
            )
        if not identity_valid(identity=identity, authorization=authorization):
            raise ValueError(
                f"Invalid identity {identity} given for credential retraction"
            )
