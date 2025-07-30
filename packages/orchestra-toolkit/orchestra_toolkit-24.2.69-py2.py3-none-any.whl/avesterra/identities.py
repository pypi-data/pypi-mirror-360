""" Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""
import avesterra.compartments as compartments
from avesterra.outlets import delete_outlet, create_outlet
import avesterra.features as features
from avesterra.avial import *
from avesterra.predefined import authentication_outlet
import avesterra.facts as facts
import avesterra.tokens as tokens

AvIdentity = AvEntity


def create_identity(
    name: str,
    key: str,
    email: str,
    authorization: AvAuthorization,
) -> AvEntity:
    token: AvAuthorization = AvAuthorization.random()
    authority: AvAuthorization = AvAuthorization.random()
    validation: str = str(AvAuthorization.random())

    if key == NULL_KEY:
        raise ValueError("null identity key not allowed")

    if not features.feature_member(
        entity=authentication_outlet,
        attribute=AvAttribute.IDENTITY,
        key=key,
        authorization=authorization,
    ):
        # Create identity entity
        identity: AvEntity = create_entity(
            name=name,
            key=key,
            context=AvContext.AVESTERRA,
            category=AvCategory.AVESTERRA,
            klass=AvClass.IDENTITY,
            outlet=authentication_outlet,
            authorization=authorization,
        )

        # Authorize identity

        # Connect compartment adapter to identity
        connect_method(
            entity=identity, outlet=authentication_outlet, authorization=authorization
        )

        # Reference identity so it can survive a reboot
        reference_entity(entity=identity, authorization=authorization)

        # Invoke authentication adapter
        invoke_entity(
            entity=identity, method=AvMethod.CREATE, authorization=authorization
        )

        # Create identity outlet
        ident_outlet: AvEntity = create_outlet(
            name=name,
            key=key,
            context=AvContext.AVESTERRA,
            category=AvCategory.AVESTERRA,
            klass=AvClass.AVESTERRA,
            authorization=authorization,
        )

        # Change identity outlet authority to new identity authority
        change_entity(
            entity=ident_outlet, authority=authority, authorization=authorization
        )

        # Reference identity outlet so it can survive a reboot
        reference_entity(entity=ident_outlet, authorization=authorization)

        # Setup identity fields
        facts.set_fact(
            entity=identity,
            attribute=AvAttribute.TOKEN,
            value=AvValue.encode_string(str(token)),
            authorization=authorization,
        )
        facts.set_fact(
            entity=identity,
            attribute=AvAttribute.AUTHORITY,
            value=AvValue.encode_string(str(authority)),
            authorization=authorization,
        )
        facts.set_fact(
            entity=identity,
            attribute=AvAttribute.OUTLET,
            value=AvValue.encode(ident_outlet),
            authorization=authorization,
        )
        facts.set_fact(
            entity=identity,
            attribute=AvAttribute.COMPARTMENT,
            value=NULL_VALUE,
            authorization=authorization,
        )
        facts.set_fact(
            entity=identity,
            attribute=AvAttribute.EMAIL,
            value=AvValue.encode_string(email),
            authorization=authorization,
        )
        facts.set_fact(
            entity=identity,
            attribute=AvAttribute.PASSWORD,
            value=AvValue.encode_string(""),
            authorization=authorization,
        )
        facts.set_fact(
            entity=identity,
            attribute=AvAttribute.STATE,
            value=AvValue.encode_string("WARNING_STATE"),
            authorization=authorization,
        )
        facts.set_fact(
            entity=identity,
            attribute=AvAttribute.VALIDATION,
            value=AvValue.encode_string(validation),
            authorization=authorization,
        )

        # Self subscribe identity_outlet
        subscribe_event(
            entity=ident_outlet, outlet=ident_outlet, authorization=authority
        )

        # Put reference to identity in the authentication outlet
        features.set_feature(
            entity=authentication_outlet,
            attribute=AvAttribute.IDENTITY,
            name=name,
            key=key,
            value=AvValue.encode(identity),
            authorization=authorization,
        )

        # Enable map the identity's token to its
        # authority
        tokens.instate(token=token, authority=authority, authorization=authorization)
        return identity
    else:
        raise AuthorizationError("identity already exists")


def delete_identity(identity: AvEntity, authorization: AvAuthorization):
    # Get key of identity
    identity_key: str = entity_key(entity=identity, authorization=authorization)

    if identity_valid(identity=identity, authorization=authorization):
        # Get token of identity
        token: AvAuthorization = AvAuthorization(
            facts.fact_value(
                entity=identity,
                attribute=AvAttribute.TOKEN,
                authorization=authorization,
            ).decode_string()
        )

        # Disable the identity's token, so it cannot be used
        # as a substitute for the entity's authority
        tokens.destate(token=token, authorization=authorization)

        # Get identity's authority
        authority: AvAuthorization = AvAuthorization(
            facts.get_fact(
                entity=identity,
                attribute=AvAttribute.AUTHORITY,
                authorization=authorization,
            ).decode_string()
        )

        # Prevents identity's authority from being able to access
        # NULL ENTITY(Where token -> authority) mappings are stored
        deauthorize_entity(
            entity=NULL_ENTITY, authority=authority, authorization=authorization
        )

        # Make identity leave all compartments
        # that it is a member of
        while (
            features.feature_count(
                entity=identity,
                attribute=AvAttribute.COMPARTMENT,
                authorization=authorization,
            )
            != 0
        ):
            compartment: AvEntity = features.feature_value(
                entity=identity,
                attribute=AvAttribute.COMPARTMENT,
                authorization=authorization,
            ).decode_entity()

            compartments.revoke_compartment(
                compartment=compartment, identity=identity, authorization=authorization
            )

        # Remove identity from the compartment adapter
        features.exclude_feature(
            entity=authentication_outlet,
            attribute=AvAttribute.IDENTITY,
            key=identity_key,
            authorization=authorization,
        )

        # Get identity outlet from identity
        outlet: AvEntity = facts.fact_value(
            entity=identity, attribute=AvAttribute.OUTLET, authorization=authorization
        ).decode_entity()

        # Dereference identity outlet
        # so that it can be deleted
        dereference_entity(entity=outlet, authorization=authorization)

        # Delete identity outlet
        delete_outlet(outlet=outlet, authorization=authorization)

        # Dereference identity so that it can
        # be deleted
        dereference_entity(entity=identity, authorization=authorization)

        # Delete identity
        delete_entity(entity=identity, authorization=authorization)
    else:
        raise AuthorizationError("invalid identity")


def reset_password(identity: AvEntity, authorization: AvAuthorization):
    validation: str = str(AvAuthorization.random())

    if identity_valid(identity=identity, authorization=authorization):
        # Empty out password hash
        facts.set_fact(
            entity=identity,
            attribute=AvAttribute.PASSWORD,
            value=AvValue.encode_string(""),
            authorization=authorization,
        )

        # Set new validation token
        facts.set_fact(
            entity=identity,
            attribute=AvAttribute.VALIDATION,
            value=AvValue.encode_string(str(validation)),
            authorization=authorization,
        )

        # Put entity into warning state; must validate
        # to put it into "GOOD" state
        facts.set_fact(
            entity=identity,
            attribute=AvAttribute.STATE,
            value=AvValue.encode_string("WARNING_STATE"),
            authorization=authorization,
        )
    else:
        raise AuthorizationError("invalid identity")


def identity_authority(
    identity: AvEntity, authorization: AvAuthorization
) -> AvAuthorization:
    if identity_valid(identity=identity, authorization=authorization):
        return AvAuthorization(
            facts.fact_value(
                entity=identity,
                attribute=AvAttribute.AUTHORITY,
                authorization=authorization,
            ).decode_string()
        )
    else:
        raise AuthorizationError("invalid identity")


def authenticated_authority(
    identity_key: AvKey, ident_token: AvAuthorization
) -> AvAuthorization:
    return AvAuthorization(
        invoke_entity(
            entity=authentication_outlet,
            method=AvMethod.GET,
            attribute=AvAttribute.AUTHENTICATION,
            key=identity_key,
            value=AvValue.encode_string(str(ident_token)),
            authorization=VERIFY_AUTHORIZATION,
        ).decode_string()
    )


def identity_token(
    identity: AvEntity, authorization: AvAuthorization
) -> AvAuthorization:
    if identity_valid(identity=identity, authorization=authorization):
        return AvAuthorization(
            facts.fact_value(
                entity=identity,
                attribute=AvAttribute.TOKEN,
                authorization=authorization,
            ).decode_string()
        )
    else:
        raise AuthorizationError("invalid identity")


def authenticated_token(identity_key: AvKey, password: str) -> AvAuthorization:
    return AvAuthorization(
        invoke_entity(
            entity=authentication_outlet,
            method=AvMethod.GET,
            attribute=AvAttribute.IDENTITY,
            key=identity_key,
            value=AvValue.encode_string(password),
            authorization=VERIFY_AUTHORIZATION,
        ).decode_string()
    )


def identity_outlet(identity: AvEntity, authorization: AvAuthorization) -> AvEntity:
    if identity_valid(identity=identity, authorization=authorization):
        return facts.fact_value(
            entity=identity, attribute=AvAttribute.OUTLET, authorization=authorization
        ).decode_entity()
    else:
        raise AuthorizationError("Invalid identity")


def change_password(
    identity_key: str,
    old_password: str,
    new_password: str,
    ident_token: AvAuthorization,
):
    password = f"{old_password.ljust(32, ' ')}{new_password.ljust(32, ' ')}"

    invoke_entity(
        entity=authentication_outlet,
        method=AvMethod.SET,
        name=password,
        key=identity_key,
        value=AvValue.encode_string(str(ident_token)),
        authorization=VERIFY_AUTHORIZATION,
    )


def validate_identity_trick(identity: AvEntity, authorization: AvAuthorization):
    facts.set_fact(
        entity=identity,
        attribute=AvAttribute.STATE,
        value=AvValue.encode_string("GOOD_STATE"),
        authorization=authorization,
    )


def lookup_identity(key: str, authorization: AvAuthorization) -> AvEntity:
    if features.feature_member(
        entity=authentication_outlet,
        attribute=AvAttribute.IDENTITY,
        key=key,
        authorization=authorization,
    ):
        return features.feature_value(
            entity=authentication_outlet,
            attribute=AvAttribute.IDENTITY,
            key=key,
            authorization=authorization,
        ).decode_entity()
    else:
        return NULL_ENTITY


def identity_valid(identity: AvEntity, authorization: AvAuthorization) -> bool:
    return (
        lookup_identity(
            key=entity_key(entity=identity, authorization=authorization),
            authorization=authorization,
        )
        != NULL_ENTITY
    )


def identity_state(identity: AvEntity, authorization: AvAuthorization) -> AvState:
    return AvState[
        facts.fact_value(entity=identity, authorization=authorization).decode_integer()
    ]


def authenticated_outlet(identity_key: str, ident_token: AvAuthorization) -> AvEntity:
    return invoke_entity(
        entity=authentication_outlet,
        method=AvMethod.GET,
        attribute=AvAttribute.OUTLET,
        name=identity_key,
        value=AvValue.encode_string(str(ident_token)),
        authorization=VERIFY_AUTHORIZATION,
    ).decode_entity()
