.. _aiorest-ws-serializing:

Model serializing
=================

.. currentmodule:: aiorest_ws.db.orm

Serializers which will be described below give to a programmer opportunities to convert complex
data structures like model instances of certain ORM to the default Python datatypes. The result
of this processing can be returned to a user in JSON, XML or any other formats. These serializers
also provide deserializing mechanisms which can be used for parsing and validating user input data
that will be used for to work with ORMs further.

These serializers largely based on ideas of Django REST Framework. In this way a lot of
functionality that will be described further will coincide with this library.

At the moment aiorest-ws have support with the following ORMs:

- Django
- SQLAlchemy

You can find corresponding modules for each of mentioned ORMs in ``aiorest_ws.db.orm.*`` namespace.

Serializers
-----------

Defining model serializer
^^^^^^^^^^^^^^^^^^^^^^^^^

Serializing
^^^^^^^^^^^

Deserializing
^^^^^^^^^^^^^

Validating and saving instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Partial instance updates
^^^^^^^^^^^^^^^^^^^^^^^^

Work with multiple objects
^^^^^^^^^^^^^^^^^^^^^^^^^^

Work with nested objects
^^^^^^^^^^^^^^^^^^^^^^^^

Serializer fields
-----------------

BigIntegerField
^^^^^^^^^^^^^^^

BooleanField
^^^^^^^^^^^^

CharField
^^^^^^^^^

ChoiceField
^^^^^^^^^^^

CreateOnlyDefault
^^^^^^^^^^^^^^^^^

DateField
^^^^^^^^^

DateTimeField
^^^^^^^^^^^^^

DecimalField
^^^^^^^^^^^^

DictField
^^^^^^^^^

DurationField
^^^^^^^^^^^^^

EmailField
^^^^^^^^^^

EnumField
^^^^^^^^^

FileField
^^^^^^^^^

FilePathField
^^^^^^^^^^^^^

FloatField
^^^^^^^^^^

HStoreField
^^^^^^^^^^^

IPAddressField
^^^^^^^^^^^^^^

ImageField
^^^^^^^^^^

IntegerField
^^^^^^^^^^^^

IntervalField
^^^^^^^^^^^^^

JSONField
^^^^^^^^^

LargeBinaryField
^^^^^^^^^^^^^^^^

ListField
^^^^^^^^^

ModelField
^^^^^^^^^^

MultipleChoiceField
^^^^^^^^^^^^^^^^^^^

NullBooleanField
^^^^^^^^^^^^^^^^

PickleField
^^^^^^^^^^^

ReadOnlyField
^^^^^^^^^^^^^

RegexField
^^^^^^^^^^

SerializerMethodField
^^^^^^^^^^^^^^^^^^^^^

SlugField
^^^^^^^^^

SmallIntegerField
^^^^^^^^^^^^^^^^^

TimeField
^^^^^^^^^

URLField
^^^^^^^^

UUIDField
^^^^^^^^^

Serializer relation fields
--------------------------

PrimaryKeyRelatedField
^^^^^^^^^^^^^^^^^^^^^^

HyperlinkedRelatedField
^^^^^^^^^^^^^^^^^^^^^^^

HyperlinkedIdentityField
^^^^^^^^^^^^^^^^^^^^^^^^

StringRelatedField
^^^^^^^^^^^^^^^^^^

SlugRelatedField
^^^^^^^^^^^^^^^^
