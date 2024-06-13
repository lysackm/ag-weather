""" Options:
Date: 2024-04-16 18:39:01
Version: 6.02
Tip: To override a DTO option, remove "#" prefix before updating
BaseUrl: https://mbaqts-prod.aquaticinformatics.net/AQUARIUS/Publish/v2

#GlobalNamespace:
#AddServiceStackTypes: True
#AddResponseStatus: False
#AddImplicitVersion:
#AddDescriptionAsComments: True
IncludeTypes: PostSession.*
#ExcludeTypes:
#DefaultImports: datetime,decimal,marshmallow.fields:*,servicestack:*,typing:*,dataclasses:dataclass/field,dataclasses_json:dataclass_json/LetterCase/Undefined/config,enum:Enum/IntEnum
#DataClass:
#DataClassJson:
"""

import datetime
import decimal
from marshmallow.fields import *
from servicestack import *
from typing import *
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase, Undefined, config
from enum import Enum, IntEnum


# @Route("/session", "POST")
@dataclass_json(letter_case=LetterCase.PASCAL, undefined=Undefined.EXCLUDE)
@dataclass
class PostSession(IReturn[str]):
    # @ApiMember(Description="Username")
    username: Optional[str] = None
    """
    Username
    """

    # @ApiMember(Description="Encrypted password")
    encrypted_password: Optional[str] = None
    """
    Encrypted password
    """

    # @ApiMember(Description="Optional locale. Defaults to English")
    locale: Optional[str] = None
    """
    Optional locale. Defaults to English
    """
