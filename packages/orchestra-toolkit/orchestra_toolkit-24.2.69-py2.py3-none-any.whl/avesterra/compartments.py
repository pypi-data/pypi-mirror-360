""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from avesterra.outlets import delete_outlet
import avesterra.identities as identities
import avesterra.features as features
from avesterra.avial import *
from avesterra.predefined import authentication_outlet
import avesterra.facts as facts
import avesterra.tokens as tokens

AvCompartment = AvEntity


def create_compartment(name: str, key: str, authorization: AvAuthorization) -> AvEntity:
    if not features.feature_member(
        entity=authentication_outlet,
        attribute=AvAttribute.COMPARTMENT,
        key=key,
        authorization=authorization,
    ):
        token: AvAuthorization = AvAuthorization.random()
        authority: AvAuthorization = AvAuthorization.random()

        # Create compartment that is attached to compartment adapter
        compartment_entity: AvEntity = create_entity(
            name=name,
            key=key,
            context=AvContext.AVESTERRA,
            category=AvCategory.AVESTERRA,
            klass=AvClass.COMPARTMENT,
            outlet=authentication_outlet,
            authorization=authorization,
        )

        # Connect compartment entity to compartment adapter
        connect_method(
            entity=compartment_entity,
            outlet=authentication_outlet,
            authorization=authorization,
        )

        # Invoke create compartment method on compartment adapter
        invoke_entity(
            entity=compartment_entity,
            method=AvMethod.CREATE,
            authorization=authorization,
        )

        # Reference compartment so that it doesn't vanish on server reboot
        reference_entity(entity=compartment_entity, authorization=authorization)

        # Create compartment "outlet"
        comp_outlet: AvEntity = create_entity(
            name=name,
            key=key,
            context=AvContext.AVESTERRA,
            category=AvCategory.AVESTERRA,
            klass=AvClass.AVESTERRA,
            outlet=authentication_outlet,
            authorization=authorization,
        )
        activate_entity(outlet=comp_outlet, authorization=authorization)

        # Change authority of entity to `authority`
        change_entity(
            entity=comp_outlet, authority=authority, authorization=authorization
        )

        # Reference compartment outlet, so it doesn't get rebooted
        # into oblivion
        reference_entity(entity=comp_outlet, authorization=authorization)

        # Setup compartment fields on compartment entity
        facts.set_fact(
            entity=compartment_entity,
            attribute=AvAttribute.OUTLET,
            value=AvValue.encode(comp_outlet),
            authorization=authorization,
        )

        facts.set_fact(
            entity=compartment_entity,
            attribute=AvAttribute.TOKEN,
            value=AvValue.encode_string(str(token)),
            authorization=authorization,
        )

        facts.set_fact(
            entity=compartment_entity,
            attribute=AvAttribute.AUTHORITY,
            value=AvValue.encode_string(str(authority)),
            authorization=authorization,
        )

        facts.set_fact(
            entity=compartment_entity,
            attribute=AvAttribute.IDENTITY,
            value=NULL_VALUE,
            authorization=authorization,
        )

        features.set_feature(
            entity=authentication_outlet,
            attribute=AvAttribute.COMPARTMENT,
            name=name,
            key=str(key),
            value=AvValue.encode(compartment_entity),
            authorization=authorization,
        )

        features.set_feature(
            entity=authentication_outlet,
            attribute=AvAttribute.KEY,
            name=name,
            key=str(token),
            value=AvValue.encode_string(key),
            authorization=authorization,
        )

        # Allow authority of compartment to invoke
        # on the NULL_ENTITY(Place where tokens are stored)
        authorize_entity(
            entity=NULL_ENTITY,
            restrictions=FALSE_PARAMETER,
            authority=authority,
            authorization=authorization,
        )

        # Enable token -> authority mapping in AvesTerra
        tokens.instate(
            server=NULL_ENTITY,
            token=token,
            authority=authority,
            authorization=authorization,
        )

        return compartment_entity
    else:
        raise AvesTerraError("Compartment already exists")


def delete_compartment(compartment: AvEntity, authorization: AvAuthorization):
    comp_key: AvKey = entity_key(entity=compartment, authorization=authorization)
    if compartment_valid(compartment=compartment, authorization=authorization):
        # Get compartment authority
        authority: AvAuthorization = compartment_authority(
            compartment=compartment, authorization=authorization
        )

        # Get compartment outlet
        comp_outlet: AvEntity = facts.fact_value(
            entity=compartment,
            attribute=AvAttribute.OUTLET,
            authorization=authorization,
        ).decode_entity()

        # De-authorize compartment auth from accessing NULL_ENTITY(token -> authority mapping)
        deauthorize_entity(
            entity=NULL_ENTITY, authority=authority, authorization=authorization
        )

        # Dereference compartment outlet
        dereference_entity(entity=comp_outlet, authorization=authorization)

        # Delete compartment outlet
        delete_outlet(outlet=comp_outlet, authorization=authorization)

        # Remove identitys from compartment entity
        while (
            features.feature_count(
                entity=compartment,
                attribute=AvAttribute.IDENTITY,
                authorization=authorization,
            )
            != 0
        ):
            # Get identity key from compartment identity feature
            identity_key: str = features.feature_key(
                entity=compartment,
                attribute=AvAttribute.IDENTITY,
                authorization=authorization,
            )

            # Get identity from identity key
            identity: AvEntity = identities.lookup_identity(
                key=identity_key, authorization=authorization
            )

            # Revoke compartment access from identity
            revoke_compartment(
                compartment=compartment, identity=identity, authorization=authorization
            )

        # Remove compartment from compartment
        # adapter outlet
        features.exclude_feature(
            entity=authentication_outlet,
            attribute=AvAttribute.COMPARTMENT,
            key=comp_key,
            authorization=authorization,
        )

        # Dereference compartment entity to enable deletion
        dereference_entity(entity=compartment, authorization=authorization)

        # Delete compartment entity from AvesTerra
        delete_entity(entity=compartment, authorization=authorization)
    else:
        raise AuthorizationError("invalid compartment")


def grant_compartment(
    compartment: AvEntity, identity: AvEntity, authorization: AvAuthorization
):
    comp_key: str = entity_key(entity=compartment, authorization=authorization)

    identity_key: str = entity_key(entity=identity, authorization=authorization)

    if compartment_valid(
        compartment=compartment, authorization=authorization
    ) and identities.identity_valid(identity=identity, authorization=authorization):
        if not features.feature_member(
            entity=compartment,
            attribute=AvAttribute.IDENTITY,
            key=identity_key,
            authorization=authorization,
        ):
            # Generate compartment token for identity
            new_token = AvAuthorization.random()

            # Get compartment authority
            comp_authority: AvAuthorization = compartment_authority(
                compartment=compartment, authorization=authorization
            )

            # Get compartment outlet
            comp_outlet: AvEntity = compartment_outlet(
                compartment=compartment, authorization=authorization
            )

            # Get identity authority
            ident_authority: AvAuthorization = identities.identity_authority(
                identity=identity, authorization=authorization
            )

            # Get identity outlet
            ident_outlet: AvEntity = identities.identity_outlet(
                identity=identity, authorization=authorization
            )

            features.set_feature(
                entity=compartment,
                attribute=AvAttribute.IDENTITY,
                key=identity_key,
                value=AvValue.encode(identity),
                authorization=authorization,
            )

            features.set_feature(
                entity=compartment,
                attribute=AvAttribute.AUTHORIZATION,
                key=identity_key,
                value=AvValue.encode_string(str(new_token)),
                authorization=authorization,
            )

            features.set_feature(
                entity=identity,
                attribute=AvAttribute.COMPARTMENT,
                key=comp_key,
                value=AvValue.encode(compartment),
                authorization=authorization,
            )

            # Allow the compartment authority
            # to access the identity outlet
            authorize_entity(
                entity=ident_outlet,
                authority=comp_authority,
                authorization=ident_authority,
            )

            # Subscribe identity outlet to the compartment outlet
            subscribe_event(
                entity=comp_outlet, outlet=ident_outlet, authorization=authorization
            )

            # Allow the newly generated compartment token
            # for the identity to map to the compartment
            # authority
            tokens.instate(
                server=NULL_ENTITY,
                token=new_token,
                authority=comp_authority,
                authorization=authorization,
            )
    else:
        if not compartment_valid(compartment=compartment, authorization=authorization):
            raise AuthorizationError("invalid compartment/identity")


def revoke_compartment(
    compartment: AvEntity, identity: AvEntity, authorization: AvAuthorization
):
    comp_key: str = entity_key(entity=compartment, authorization=authorization)
    identity_key: str = entity_key(entity=identity, authorization=authorization)

    if compartment_valid(
        compartment=compartment, authorization=authorization
    ) and features.feature_member(
        entity=compartment,
        attribute=AvAttribute.IDENTITY,
        key=identity_key,
        authorization=authorization,
    ):
        token: AvAuthorization = AvAuthorization(
            features.feature_value(
                entity=compartment,
                attribute=AvAttribute.AUTHORIZATION,
                key=identity_key,
                authorization=authorization,
            ).decode_string()
        )

        tokens.destate(server=NULL_ENTITY, token=token, authorization=authorization)

        comp_authority: AvAuthorization = compartment_authority(
            compartment=compartment, authorization=authorization
        )
        comp_outlet: AvEntity = compartment_outlet(
            compartment=compartment, authorization=authorization
        )

        ident_authority: AvAuthorization = identities.identity_authority(
            identity=identity, authorization=authorization
        )
        ident_outlet: AvEntity = identities.identity_outlet(
            identity=identity, authorization=authorization
        )

        # Remove compartment access to identity
        deauthorize_entity(
            entity=ident_outlet, authority=comp_authority, authorization=ident_authority
        )

        try:
            unsubscribe_event(
                entity=comp_outlet, outlet=ident_outlet, authorization=authorization
            )
        except Exception:
            pass

        # Remove person from compartment
        features.exclude_feature(
            entity=compartment,
            attribute=AvAttribute.IDENTITY,
            key=identity_key,
            authorization=authorization,
        )
        features.exclude_feature(
            entity=compartment,
            attribute=AvAttribute.AUTHORIZATION,
            key=identity_key,
            authorization=authorization,
        )

        # Remove identity from compartment
        features.exclude_feature(
            entity=identity,
            attribute=AvAttribute.COMPARTMENT,
            key=comp_key,
            authorization=authorization,
        )
        return

    raise AuthorizationError("invalid compartment/identity")


def enable_privilege(
    compartment: AvEntity, identity: AvEntity, authorization: AvAuthorization
):
    identity_key: str = entity_key(entity=identity, authorization=authorization)

    features.set_feature(
        entity=compartment,
        attribute=AvAttribute.PRIVILEGE,
        key=identity_key,
        value=AvValue.encode(identity),
        authorization=authorization,
    )


def disable_privilege(
    compartment: AvEntity, identity: AvEntity, authorization: AvAuthorization
):
    identity_key: str = entity_key(entity=identity, authorization=authorization)

    features.exclude_feature(
        entity=compartment,
        attribute=AvAttribute.PRIVILEGE,
        key=identity_key,
        authorization=authorization,
    )


def compartment_authority(
    compartment: AvEntity, authorization: AvAuthorization
) -> AvAuthorization:
    if compartment_valid(compartment=compartment, authorization=authorization):
        return AvAuthorization(
            facts.fact_value(
                entity=compartment,
                attribute=AvAttribute.AUTHORITY,
                authorization=authorization,
            ).decode_string()
        )
    else:
        raise AuthorizationError("Invalid compartment")


def authenticated_authority(
    comp_key: AvKey, identity_key: AvKey, ident_token: AvAuthorization
) -> AvAuthorization:
    return AvAuthorization(
        invoke_entity(
            entity=authentication_outlet,
            method=AvMethod.GET,
            attribute=AvAttribute.AUTHORITY,
            name=comp_key,
            key=identity_key,
            value=AvValue.encode_string(str(ident_token)),
            authorization=VERIFY_AUTHORIZATION,
        ).decode_string()
    )


def compartment_key(token: AvAuthorization):
    return invoke_entity(
        entity=authentication_outlet,
        method=AvMethod.GET,
        attribute=AvAttribute.KEY,
        name=NULL_NAME,
        key=str(token),
        authorization=VERIFY_AUTHORIZATION,
    ).decode()


def compartment_token(
    compartment: AvEntity,
    authorization: AvAuthorization,
):
    if compartment_valid(compartment=compartment, authorization=authorization):
        return AvAuthorization(
            facts.fact_value(
                entity=compartment,
                attribute=AvAttribute.TOKEN,
                authorization=authorization,
            ).decode_string()
        )
    else:
        raise AuthorizationError("invalid compartment")


def authenticated_token(
    comp_key: AvKey, identity_key: AvKey, ident_token: AvAuthorization
) -> AvAuthorization:
    return AvAuthorization(
        invoke_entity(
            entity=authentication_outlet,
            method=AvMethod.GET,
            attribute=AvAttribute.COMPARTMENT,
            name=comp_key,
            key=identity_key,
            value=AvValue.encode_string(str(ident_token)),
            authorization=VERIFY_AUTHORIZATION,
        ).decode_string()
    )


def compartment_outlet(
    compartment: AvEntity, authorization: AvAuthorization
) -> AvEntity:
    if compartment_valid(compartment=compartment, authorization=authorization):
        return facts.fact_value(
            entity=compartment,
            attribute=AvAttribute.OUTLET,
            authorization=authorization,
        ).decode_entity()
    else:
        raise AuthorizationError("Invalid compartment")


def lookup_compartment(key: str, authorization: AvAuthorization) -> AvEntity:
    if features.feature_member(
        entity=authentication_outlet,
        attribute=AvAttribute.COMPARTMENT,
        key=key,
        authorization=authorization,
    ):
        return features.feature_value(
            entity=authentication_outlet,
            attribute=AvAttribute.COMPARTMENT,
            key=key,
            authorization=authorization,
        ).decode_entity()
    else:
        return NULL_ENTITY


def compartment_valid(compartment: AvEntity, authorization: AvAuthorization) -> bool:
    return (
        lookup_compartment(
            key=entity_key(entity=compartment, authorization=authorization),
            authorization=authorization,
        )
        != NULL_ENTITY
    )


def authenticated_outlet(comp_key: str, comp_token: AvAuthorization) -> AvEntity:
    return invoke_entity(
        entity=authentication_outlet,
        method=AvMethod.GET,
        attribute=AvAttribute.OUTLET,
        name=comp_key,
        value=AvValue.encode_string(str(comp_token)),
        authorization=VERIFY_AUTHORIZATION,
    ).decode_entity()
