from schematics.models import Model
from schematics.types import StringType, EmailType, BaseType
from schematics.transforms import blacklist


class ObjectIdType(BaseType):
    """
    pymongo ObjectID type
    """
    def to_native(self, value, context=None):
        return str(value)


class User(Model):
    """
    User domain model
    """
    _id = ObjectIdType()
    account_key = StringType(max_length=100)
    email = EmailType(required=True, max_length=200)
    full_name = StringType(max_length=200)
    metadata = StringType(max_length=2000)
    password = StringType(required=True, max_length=100)
    password_salt = StringType()

    class Options:
        roles = {'default': blacklist('_id', 'password', 'password_salt')}
        serialize_when_none = False
