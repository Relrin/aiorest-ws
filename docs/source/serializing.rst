.. _aiorest-ws-serializing:

Model serializing
=================

.. currentmodule:: aiorest_ws.db.orm

Serializers which will be described below give to a programmer opportunities to convert complex
data structures like model instances of certain ORM to the default Python datatypes. The result
of this processing can be returned to a user in JSON, XML or any other formats. These serializers
also provide deserializing mechanisms which can be used for parsing and validating user input data
that will be used for to work with ORMs further.

These serializers largely based on ideas and concepts of Django REST Framework. In this way a lot
of functionality that will be described further will coincide with this library.

At the moment aiorest-ws have support with the following ORMs:

- Django
- SQLAlchemy

You can find corresponding modules for each of mentioned ORMs in ``aiorest_ws.db.orm.*`` namespace.

Model serializers
-----------------
The aiorest-ws library provides :class:`ModelSerializer` classes which can be used for serializing
(or deserializing) your model instances to a some specific format. Its can be used for processing
of model instances which have taken from a database.

Defining model serializer
^^^^^^^^^^^^^^^^^^^^^^^^^
Let's suppose that we have a some class which has certain functionality. For example it could be a
class that storing data about a registered user:

.. code-block:: python

    from django.db import models

    class User(models.Model):
        self.username = models.CharField(max_length=255, unique=True)
        self.email = models.EmailField()
        self.logged_at = models.DateTimeField(auto_now=True)

After this we will declare a serializer class which is used for serializing and deserializing
some data that converted to :class:`User` objects:

.. code-block:: python

    from aiorest_ws.db.orm.django import serializers

    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User

That's all! We have described our simplest serializer class that giving opportunities to work
with :class:`User` instances. As you can see there, we have declared :class:`Meta` class, that is
storing a link to the :class:`User` model. When we will put some data to the serializer instance
(or otherwise, update data), serializer will parse specified model and extract fields that will
be processed.

Serializing
^^^^^^^^^^^
Serialization mechanism let us to convert complex types into Python language types. So for it is
enough pass an existing object into a serializer instance and get ``data`` attribute after creating
serializer. For example:

.. code-block:: python

    user = User.objects.create(username='nayton', email='nayton@example.com')
    serializer = UserSerializer(user)
    serializer.data
    # {'pk': 1, 'username': 'nayton', 'email': 'nayton@example.com', 'logged_at': '2016-11-29T21:13:31.039488'}

As you can see, we have converted passed object into dictionary. So it now remains to make an
additional step, that allow to transmit the data through a network. For instance we can render it
into JSON:

.. code-block:: python

    from aiorest_ws.renderers import JSONRenderer

    json = JSONRenderer().render(serializer.data)
    json
    # b'{"pk": 1, "username": "nayton", "email": "nayton@example.com", "logged_at": "2016-11-29T21:13:31.039488"}'

Deserializing
^^^^^^^^^^^^^
Deserializing data is very useful feature when you want to get information after users action or
from 3rd party APIs and save it in a database as some model instances. For using this feature
enough to use already declared serializer class:

.. code-block:: python

    data = {"username": "new_user", "email": "new_user@example.com", "logged_at": "2016-11-29T21:15:31.078217"}
    serializer = UserSerializer(data=data)
    serializer.is_valid()
    # True
    serializer.validated_data
    # {'username': 'new_user', 'email': 'new_user@example.com', 'logged_at': datetime.datetime(2016, 11, 29, 21, 15, 31, 78217)}

Saving instances
^^^^^^^^^^^^^^^^
In some cases if you want to return created object instances which based on the validated data
then you will need to implement ``.create()`` and/or ``.update()`` methods. For example with
Django ORM it can be looks like:

.. code-block:: python

    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User

        def create(self, validated_data):
            return User.objects.create(**validated_data)

        def update(self, instance, validated_data):
            instance.username = validated_data.get('username', instance.username)
            instance.email = validated_data.get('email', instance.email)
            instance.logged_at = validated_data.get('logged_at', instance.logged_at)
            instance.save()
            return instance

After then we implemented ``.save()`` method, it will return an object instance, based on the
validated data:

.. code-block:: python

    user = serializer.save()

Worth noting that instances of :class:`ModelSerializer` class can accept instance of a model as the
an argument which is can be updated further. It leads to two different calls which can be used:

.. code-block:: python

    # The first case: `.save()` will create a new instance.
    serializer = UserSerializer(data=data)

    # The second case: `.save()` will update the existing instance.
    serializer = UserSerializer(user, data=data)

Custom implementation for ``.create`` and ``.update()`` is optional. Override it only when it
necessary for your use cases. You can implement one, both or neither of them for your own model
serializer.

Passing additional attributes to .save()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sometimes you can caught in the situation when necessary to pass additional data to the ``.save()``
method. These additional data can be represented like timestamps, session ids or anything else that
is not part of the validated data. For solving this issue you can just include additional keyword
arguments when calling ``.save()`` method. For example:

.. code-block:: python

    serializer.save(session_id=request.data['session_id'])

Each additional keyword arguments will be included in the ``serializer.validated_data`` argument
when ``.create()`` or ``.update()`` are called.

Overriding .save() directly
~~~~~~~~~~~~~~~~~~~~~~~~~~~
In some cases you doesn't want call the ``.create()`` or ``.update()`` methods, because in some use
case you want to do some useful work instead of them.

The clear example for it is a feedback form which is filled by a user on your website. After a
moment when you have taken the form, you are going to send a message to your administration team
from a server with some text instead of saving or updating model instance. For example it might
look like this:

.. code-block:: python

    class FeedbackMessageSerializer(serializers.ModelSerializer):

        class Meta:
            model = FeedbackMessage

        def save(self):
            email = self.validated_data['email']
            subject = self.validated_data['subject']
            message = self.validated_data['message']
            send_email(from=email, subject=subject, message=message)

Keep in mind that in this case we have a direct access to the serializer ``.validated_data`` attribute.

Validating
^^^^^^^^^^
When deserializing data, you always should to call ``.is_valid()`` method. This method will
validate passed data to a serializer instance and will return ``True`` value when the passed data
are correct. Otherwise will be returned ``False`` value and all occurred errors during the
validation process will be available through ``.errors`` property where each element representing
the resulting error messages. For example:

.. code-block:: python

    data = {"username": "nayton", "email": "string", "logged_at": "2016-11-30T14:43:12.174129"}
    serializer = UserSerializer(data=data)
    serializer.is_valid()
    # False
    serializer.errors
    # {'username': ['User already exists.'], 'email': ['Enter a valid e-mail address.']}

Raising an exception on invalid data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Our ``.is_valid()`` method also can get an optional ``raise_exception`` flag that allow to raise a
``aiorest_ws.db.orm.exceptions.ValidationError`` exception when returned any validation errors. For
example:

.. code-block:: python

    serializer.is_valid(raise_exception=True)

Field-level validation
~~~~~~~~~~~~~~~~~~~~~~
Sometimes you might need to make additional checks for a certain field during the validation
process. You can apply this checks by adding ``.validate_<field_name>()`` to your
:class:`ModelSerializer` subclass. Each custom field-level validation method should return the
validated value or raise a :class:`ValidationError`. For example:

.. code-block:: python

    from aiorest_ws.db.orm.django import serializers
    from aiorest_ws.db.orm.exceptions import ValidationError

    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User

        def validate_username(self, value):
            if value.lower() == "admin":
                raise ValidationError("Username cannot be set to 'admin'.")
            return value

.. note::

    If ``<field_name>`` is declared in your serializer with parameter ``required=False`` then
    this validation method will not apply if this field is not included.

Object-level validation
~~~~~~~~~~~~~~~~~~~~~~~
For a case when necessary to implement complex validation where are using multiple fields, you will
need to implement ``.validate()`` method in your :class:`ModelSerialize` subclass. This method takes
a single argument which is represented as a dictionary of field values. As well this method also
should return validated values or raise а :class:`ValidationError` exception. For example:

.. code-block:: python

    from aiorest_ws.db.orm.django import serializers
    from aiorest_ws.db.orm.exceptions import ValidationError

    class MovieSessionSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=50)
        description = serializers.CharField(max_length=255)
        start = serializers.DateTimeField()
        end = serializers.DateTimeField()

        class Meta:
            model = MovieSession

        def validate(self, data):
            """
            Check that the start is before the end.
            """
            if data['start'] > data['end']:
                raise ValidationError("Start timestamp cannot be greater than end.")
            return data

Validators
~~~~~~~~~~
For each certain field can be applied list of validators via declaring them on the field instance.
Those validators can be represented as functions or instances of some class. Each of them takes one
argument during the validation, for example:

.. code-block:: python

    from aiorest_ws.db.orm.django import serializers
    from aiorest_ws.db.orm.exceptions import ValidationError
    from django.core.validators import MaxLengthValidator

    def empty_string_validator(value):
        if not value.strip():
            raise ValidationError('Title cannot be empty.')

    class PageSerializer(serializers.ModelSerializer):
        title = serializers.CharField(validators=[empty_string_validator, MaxLengthValidator(50)])
        ...

Also you can apply similar checks to the complete set of field data. For using this mechanism will
be enough to specify ``validators`` attribute (as a list of used validators) in inner
:class:`Meta` class, like here:

.. code-block:: python

    from aiorest_ws.db.orm.django import serializers
    from aiorest_ws.db.orm.validators import BaseUniqueFieldValidator

    class UniqueTogetherValidator(BaseUniqueFieldValidator):
        """
        Special validator class that check on uniqueness pair of fields.
        """
        def __init__(self, queryset, fields, message=None):
            super(UniqueTogetherValidator, self).__init__(queryset, message)
            self.fields = fields

        def __call__(self, attrs):
            ...

    class TrackSerializer(serializers.ModelSerializer):
        name = serializers.CharField(max_length=100)
        duration = serializers.TimeField()
        track_number = serializers.IntegerField()
        cd_name = serializers.CharField(max_length=255)

        class Meta:
            model = Track
            validators = [
                UniqueTogetherValidator(
                    queryset=Track.objects.all(),
                    fields=('track_number', 'cd_name')
                ),
            ]

Accessing the initial data and instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
After creating an instance of a :class:`ModelSerializer` subclass you can get access to following
attributes which can be useful during validation or creating/updating objects: ``.instance`` and
``.initial_data``.

The first one, ``.instance`` attribute, can be set as the first argument of aserializer subclass
or with "instance" keyword. The passed instance can be initial object or queryset. If no initial
object is passed then the ``.instance`` attribute will be ``None``.

The second one, ``.initial_data`` attribute, can be set as the second argument of a serializer
subclass or with "data" keyword. And when you are passing data to a serializer instance, the
unmodified data will be made available as ``.initial_data``. If the ``data`` keyword argument is
not passed then the ``.initial_data`` attribute will not exist.

Partial instance updates
^^^^^^^^^^^^^^^^^^^^^^^^
By default for each serializer you must specify all required fields or it will raise validation
errors. For using partial updates you will need to pass ``partial`` flag with ``True`` value. For
example:

.. code-block:: python

    # Update `user` with partial data
    serializer = UserSerializer(user, data={'email': 'new_nayton_email@exampl.com'}, partial=True)

Dealing with nested objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^
The above examples are pretty fine demonstrating how to work with a models that have a simple
datatypes. But in most projects with which you will be work, will be have models this relations
with which also necessary to work. And you expecting that will be able to represent more complex
objects, that contains not only default datatypes.

Because each field class and :class:`ModelSerializer` subclass have the same parent
:class:`AbstractSerializer` class, you can use these model serializers for represent relationships
where one object type is nested inside another.

.. note::
    And here we have a difference with Django REST framework. The author of aiorest-ws library have
    divided the :class:`Field` class onto two different classes: model serializer and its model
    fields. This is done in order to make it easier for programmers to understand what is happening
    in the process of debugging.

.. code-block:: python

    from aiorest_ws.db.orm.django import serializers

    class CategorySerializer(serializers.ModelSerializer):
        name = serializers.CharField(max_length=255)

        class Meta:
            model = Category

    class PostSerializer(serializers.Serializer):
        category = CategorySerializer()
        title = serializers.CharField(max_length=255)
        content = serializers.CharField(max_length=3000)

        class Meta:
            model = Post

In the case if a nested serializer may accept the ``None`` value, you should pass the
``required=False`` value to this nested serializer:

.. code-block:: python

    class PostSerializer(serializers.Serializer):
        category = CategorySerializer(required=False)  # Post can be without a category
        title = serializers.CharField(max_length=255)
        content = serializers.CharField(max_length=3000)

        class Meta:
            model = Post

For a case when a nested serializer should be represented as a list of objects, specify the
``many=True`` value to the nested serializer:

.. code-block:: python

    class PostSerializer(serializers.Serializer):
        category = CategorySerializer(many=True)  # A list of categories
        title = serializers.CharField(max_length=255)
        content = serializers.CharField(max_length=3000)

        class Meta:
            model = Post

Writable nested representations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When dealing with nested representations that support deserializing the data, any errors with
nested objects will be nested under the field name of the nested object.

.. code-block:: python

    data = {'category': {'name': ''}, 'title': 'aiorest-ws docs', 'content': 'The first version of docs.'}
    serializer = PostSerializer(data=data)
    serializer.is_valid()
    # False
    serializer.errors
    # {'category': {'name': ['This field may not be blank.']}}

Similarly, the ``.validated_data`` property will include nested data structures.

Writing .create() methods for nested representations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For a case when necessary to support writable nested representations for a model serializer, you
will need to override ``.create()`` or ``.update()`` methods that giving opportunities to work with
multiple objects.

Take a look on the next example that demonstrate you how to create a :class:`Post` instance with
nested objects:

.. code-block:: python

    class PostSerializer(serializers.Serializer):
        category = CategorySerializer(many=True)
        title = serializers.CharField(max_length=255)
        content = serializers.CharField(max_length=3000)

        class Meta:
            model = Post
            fields = ('category', 'title', 'content')

        def create(self, validated_data):
            category_data = validated_data.pop('category')
            post = Post.objects.create(**validated_data)
            Category.objects.create(post=post, **category_data)
            return post

Writing .update() methods for nested representations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For a case when necessary to update an instance with nested relationships is more complex. First of
all you must decide how to handle updates to relationships. What to do if the data for model
relationship is ``None`` value, or perhaps not provided? We can use one of the following solutions:

- Set the relationship to NULL in the database.
- Delete the associated instance.
- Ignore the data and leave the instance as it is.
- Raise a validation error.

Take a look on the next example for an ``.update()`` method of :class:`PostSerializer` class:

.. code-block:: python

     def update(self, instance, validated_data):
            category_data = validated_data.pop('category')
            # Unless the application properly enforces that this field is
            # always set, the follow could raise a `DoesNotExist`, which
            # would need to be handled.
            category_instance = instance.category
            category_instance.name = category_data.get('name', 'Blog')
            category_instance.save()

            instance.title = validated_data.get('title', instance.title)
            instance.content = validated_data.get('content', instance.content)
            instance.save()

            return instance

Because the behavior of nested creates and updates can be ambiguous, and may require complex
dependencies between related models, :class:`ModelSerializer` requires you to always write these
methods explicitly. The default :class:`ModelSerializer` ``.create()`` and ``.update()`` methods do
not include support for writable nested representations.

Dealing with multiple objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For each supported ORM the :class:`ModelSerializer` class can also handle serializing or
deserializing lists of objects.

Serializing multiple objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For a case when necessary to serialize a queryset or list of objects instead of a single object
instance, just specify the ``many=True`` flag when instantiating the model serializer. You can then
specify a queryset or list of objects to be serialized.

.. code-block:: python

    queryset = Category.objects.all()
    serializer = CategorySerializer(queryset, many=True)
    serializer.data
    # [
    #     {'name': 'Documentation'},
    #     {'name': 'Features'},
    #     {'name': 'Change notes'}
    # ]

Deserializing multiple objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The default behavior for deserializing multiple objects is to support multiple object creation,
but not support multiple object updates. For more information on how to support or customize either
of these cases, see the ListSerializer documentation below.

Including extra context
^^^^^^^^^^^^^^^^^^^^^^^
In some cases you may need to provide extra context which can be used by serializer during the
validating or in addition to the object being serialized. You can do this by passing a ``context``
argument when instantiating the serializer. For example:

.. code-block:: python

    class UserSerializer(serializers.ModelSerializer):

        class Meta:
            model = User
            fields = ('username', 'email')

        def to_representation(self, instance):
            data = super(UserSerializer, self).to_representation(instance)
            data['request_id'] = self.context['request'].request_id
            return data

    serializer = UserSerializer(user, context={'request': request})
    serializer.data
    # {"username": "nayton", "email": "nayton@example.com", "request_id": "76c3d654-b804-11e6-a794-0c4de9c846b0"}

The context dictionary can be used within any serializer field logic, such as a custom
``.to_representation()`` method, by accessing the ``self.context`` attribute.

ModelSerializer
^^^^^^^^^^^^^^^
All information that described above applied for this class and its subclasses. The
:class:`ModelSerializer` class define an interface that help developers in serializing and
deserializing models of Django and SQLAlchemy ORMs.

What can :class:`ModelSerializer` class:

- Automatically extract and generate a set of fields based on the specified model.
- Apply validators (and user-defined also) for the serializer and its fields.
- Provides implementations for ``.create()`` and ``.update()`` method by default.

Example of using:

.. code-block:: python

    class UserSerializer(serializers.ModelSerializer):

        class Meta:
            model = User
            fields = ('pk', 'username', 'email', 'logged_at')


Inspecting a ModelSerializer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Model serializers provide a very helpful representation strings, that allow you to fully inspect a
state for each serializer field. This is very useful during debugging and let you understand what
kind of fields and validators are being automatically created for you.

To do so, open the you application shell, after that import the model serializer class, instantiate
it, and print the object representation:

.. code-block:: python

    >>> from app.serializers import CarSerializer
    >>> serializer = CarSerializer()
    >>> print(repr(serializer))
    ... CarSerializer():
    ...    id = IntegerField(label=ID, read_only=True)
    ...    name = CharField(max_length=30, validators=['<UniqueValidator(queryset=django_orm_example.Car.objects)>'])
    ...    manufacturer = PrimaryKeyRelatedField(label=Manufacturer, queryset=django_orm_example.Manufacturer.objects)

Specifying which fields to include
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you only want a subset of the default fields to be used in a model serializer, you can do so
using ``fields`` or ``exclude`` options, just as you would with a ModelForm in Django. It is
strongly recommended that you explicitly set all fields that should be serialized using the fields
attribute. This will make it less likely to result in unintentionally exposing data when your
models change.

For example:

.. code-block:: python

    class UserSerializer(serializers.ModelSerializer):

        class Meta:
            model = User
            fields = ('username', 'email', 'logged_at')

You can also set the fields attribute to the special value ``__all__`` to indicate that all fields
in the model should be used.

For example:

.. code-block:: python

    class UserSerializer(serializers.ModelSerializer):

        class Meta:
            model = User
            fields = '__all__'

You can set the ``exclude`` attribute to a list of fields to be excluded from the serializer.

For example:

.. code-block:: python

    class UserSerializer(serializers.ModelSerializer):

        class Meta:
            model = User
            exclude = ('logged_at', )

In the example above, if the ``User`` model had 3 fields ``username``, ``email``, and
``logged_at``, this will result in the fields ``username`` and ``email`` to be serialized.

The names in the ``fields`` and ``exclude`` attributes will normally map to model fields on the
model class.

Alternatively names in the ``fields`` options can map to properties or methods which take no arguments
that exist on the model class.

Specifying nested serialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The default :class:`ModelSerializer` uses primary keys for relationships, but you can also easily
generate nested representations using the ``depth`` option:

.. code-block:: python

    class CarSerializer(serializers.ModelSerializer):

        class Meta:
            model = Account
            fields = ('id', 'name', 'manufacturer')
            depth = 1

The ``depth`` option should be set to an integer value that indicates the depth of relationships
that should be traversed before reverting to a flat representation.

If you want to customize the way the serialization is done you'll need to define the field yourself.

Specifying fields explicitly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can add extra fields to a :class:`ModelSerializer` or override the default fields by declaring
fields on the class.

.. code-block:: python

    class CarSerializer(serializers.ModelSerializer):
        name = serializers.CharField(read_only=True)
        manufacturer = serializers.PrimaryKeyRelatedField()

        class Meta:
            model = Car

Extra fields can correspond to any property or callable on the model.

Specifying read only fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~
You may wish to specify multiple fields as read-only. Instead of adding each field explicitly with
the ``read_only=True`` attribute, you may use the shortcut Meta option, ``read_only_fields``.

This option should be a list or tuple of field names, and is declared as follows:

.. code-block:: python

    class UserSerializer(serializers.ModelSerializer):

        class Meta:
            model = User
            fields = ('username', 'email', 'logged_at')
            read_only_fields = ('email', )

Model fields which have ``editable=False`` set, and ``AutoField`` fields will be set to read-only by
default, and do not need to be added to the ``read_only_fields`` option.

Additional keyword arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
There is also a shortcut allowing you to specify arbitrary additional keyword arguments on fields,
using the ``extra_kwargs`` option. As in the case of ``read_only_fields``, this means you do not
need to explicitly declare the field on the serializer.

This option is a dictionary, mapping field names to a dictionary of keyword arguments. For example:

.. code-block:: python

    class CreateUserSerializer(serializers.ModelSerializer):

        class Meta:
            model = User
            fields = ('email', 'username', 'password')
            extra_kwargs = {'password': {'write_only': True}}

        def create(self, validated_data):
            user = User(
                email=validated_data['email'],
                username=validated_data['username']
            )
            user.set_password(validated_data['password'])
            user.save()
            return user

Relational fields
~~~~~~~~~~~~~~~~~
When serializing model instances, there are a number of different ways you might choose to
represent relationships. The default representation for :class:`ModelSerializer` is to use the
primary keys of the related instances.

Alternative representations include serializing using hyperlinks, serializing complete nested
representations, or serializing with a custom representation.

Inheritance of the 'Meta' class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The inner ``Meta`` class on serializers is not inherited from parent classes by default. This is
the same behavior as with Django's model. If you want the Meta class to inherit from a parent class
you must do so explicitly. For example:

.. code-block:: python

    class UserSerializer(MyBaseSerializer):

        class Meta(MyBaseSerializer.Meta):
            model = User

Typically we would recommend not using inheritance on inner Meta classes, but instead declaring all
options explicitly.

Customizing field mappings
~~~~~~~~~~~~~~~~~~~~~~~~~~
The :class:`ModelSerializer` class also exposes an API that you can override in order to alter how
serializer fields are automatically determined when instantiating the serializer.

Normally if a ModelSerializer does not generate the fields you need by default then you should
either add them to the class explicitly. However in some cases you may want to create a new base
class that defines how the serializer fields are created for any given model.

- ``.serializer_field_mapping``

A mapping of Django or SQLAlchemy model classes to aiorest-ws serializer classes. You can override
this mapping to alter the default serializer classes that should be used for each model class.

- ``.serializer_related_field``

This property should be the serializer field class, that is used for relational fields by default.

For :class:`ModelSerializer` this defaults to :class:`PrimaryKeyRelatedField``.

For :class:`HyperlinkedModelSerializer` this defaults to :class:`serializers.HyperlinkedRelatedField.`

- ``serializer_url_field``

The serializer field class that should be used for any url field on the serializer.

Defaults to :class:`serializers.HyperlinkedIdentityField`

- ``serializer_choice_field``

The serializer field class that should be used for any choice fields on the serializer.

Defaults to :class:`serializers.ChoiceField` for Django ORM and :class:`serializers.EnumField` for
SQLAlchemy ORM.

The field_class and field_kwargs API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The following methods are called to determine the class and keyword arguments for each field that
should be automatically included on the serializer. Each of these methods should return a two tuple
of ``(field_class, field_kwargs)``.

- ``.build_standard_field(self, field_name, model_field)``

Called to generate a serializer field that maps to a standard model field.

The default implementation returns a serializer class based on the ``serializer_field_mapping`` attribute.

- ``.build_relational_field(self, field_name, relation_info)``

Called to generate a serializer field that maps to a relational model field.

The default implementation returns a serializer class based on the ``serializer_relational_field`` attribute.

The ``relation_info`` argument is a named tuple, that contains ``model_field``, ``related_model``,
``to_many`` and ``has_through_model properties``.

- ``.build_nested_field(self, field_name, relation_info, nested_depth)``

Called to generate a serializer field that maps to a relational model field, when the ``depth``
option has been set.

The default implementation dynamically creates a nested serializer class based on either
:class:`ModelSerializer` or :class:`HyperlinkedModelSerializer`.

The ``nested_depth`` will be the value of the ``depth`` option, minus one.

The ``relation_info`` argument is a named tuple, that contains ``model_field``, ``related_model``,
``to_many`` and ``has_through_model`` properties.

- ``.build_property_field(self, field_name, model_class)``

Called to generate a serializer field that maps to a property or zero-argument method on the model class.

The default implementation returns a :class:`ReadOnlyField` class.

- ``.build_url_field(self, field_name, model_class)``

Called to generate a serializer field for the serializer's own ``url`` field. The default
implementation returns a :class:`HyperlinkedIdentityField` class.

- ``.build_unknown_field(self, field_name, model_class)``

Called when the field name did not map to any model field or model property. The default
implementation raises an error, although subclasses may customize this behavior.

HyperlinkedModelSerializer
^^^^^^^^^^^^^^^^^^^^^^^^^^
The :class:`HyperlinkedModelSerializer` class is similar to the :class:`ModelSerializer` class
except that it uses hyperlinks to represent relationships, rather than primary keys.

By default the serializer will include a ``url`` field instead of a primary key field.

The url field will be represented using a :class:`HyperlinkedIdentityField` serializer field, and
any relationships on the model will be represented using a :class:`HyperlinkedRelatedField`
serializer field.

You can explicitly include the primary key by adding it to the ``fields`` option, for example:

.. code-block:: python

    class UserSerializer(serializers.ModelSerializer):

        class Meta:
            model = User
            fields = ('url', 'username', 'email', 'logged_at')

Absolute and relative URLs
~~~~~~~~~~~~~~~~~~~~~~~~~~
When instantiating a :class:`HyperlinkedModelSerializer` you do not need to include the current
request in the serializer context as it implemented in Django REST. Just create an serialized
instance and call the ``.data`` attribute:

.. code-block:: python

    serializer = UserSerializer(user_queryset)

So, after getting a data from serializer instance, you will get absolute path to this object
instead of primary key:

.. code-block:: javascript

    "wss://127.0.0.1:8000/user/1/"

If you do want to use relative URLs, you should explicitly pass ``{'relative': True}`` to the
serializer constructor as the ``context`` argument:

.. code-block:: python

    serializer = UserSerializer(user_object, context={'relative': True})

After that you will get a relative link to an object:

.. code-block:: javascript

    "/user/1/"

How hyperlinked views are determined
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
There needs to be a way of determining which views should be used for hyperlinking to model
instances.

By default hyperlinks are expected to correspond to a view name that matches the style
``'{model_name}-detail'``, and looks up the instance by a ``pk`` keyword argument.

You can override a URL field view name and lookup field by using either, or both of, the
``view_name`` and ``lookup_field`` options in the ``extra_kwargs`` setting, like so:


.. code-block:: python

    class CarSerializer(serializers.HyperlinkedModelSerializer):

        class Meta:
            model = Account
            fields = ('car_url', 'car_model', 'factories')
            extra_kwargs = {
                'url': {'view_name': 'cars', 'lookup_field': 'car_model'}
                'factories': {'lookup_field': 'name'}
            }

Alternatively you can set the fields on the serializer explicitly. For example:

.. code-block:: python

    class CarSerializer(serializers.HyperlinkedModelSerializer):
        url = serializers.HyperlinkedIdentityField(
            view_name='cars', lookup_field='car_model'
        )
        factories = serializers.HyperlinkedRelatedField(
            view_name='factory-detail', lookup_field='name',
            many=True, read_only=True
        )

        class Meta:
            model = Account
            fields = ('url', 'car_model', 'factories')

**Tip**: Properly matching together hyperlinked representations and your URL conf can sometimes
be a bit fiddly. Printing the ``repr`` of a :class:`HyperlinkedModelSerializer` instance is a
particularly useful way to inspect exactly which view names and lookup fields the relationships
are expected to map too.

Changing the URL field name
~~~~~~~~~~~~~~~~~~~~~~~~~~~
The name of the URL field defaults to ``url``. You can override this globally, by using the
``URL_FIELD_NAME`` setting.

ListSerializer
^^^^^^^^^^^^^^
The :class:`ListSerializer` class provides the behavior for serializing and validating multiple
objects at once. You won't typically need to use :class:`ListSerializer` directly, but should instead
simply pass ``many=True`` when instantiating a serializer.

When a serializer is instantiated and ``many=True`` is passed, a :class:`ListSerializer` instance
will be created. The serializer class then becomes a child of the parent :class:`ListSerializer`.

The following argument can also be passed to a :class:`ListSerializer` field or a serializer that
is passed ``many=True``:

``allow_empty``

This is ``True`` by default, but can be set to ``False`` if you want to disallow empty lists as
valid input.

Customizing ListSerializer behavior
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
There are a few use cases when you might want to customize the :class:`ListSerializer` behavior.
For example:

- You want to provide particular validation of the lists, such as checking that one element does
  not conflict with another element in a list.

- You want to customize the create or update behavior of multiple objects.

For these cases you can modify the class that is used when ``many=True`` is passed, by using the
``list_serializer_class`` option on the serializer ``Meta`` class.

For example:

.. code-block:: python

    class CustomListSerializer(serializers.ListSerializer):
        ...

    class CustomSerializer(serializers.Serializer):
        ...
        class Meta:
            list_serializer_class = CustomListSerializer

Customizing multiple create
~~~~~~~~~~~~~~~~~~~~~~~~~~~
The default implementation for multiple object creation is to simply call ``.create()`` for each
item in the list. If you want to customize this behavior, you'll need to customize the ``.create()``
method on :class:`ListSerializer` class that is used when ``many=True`` is passed.

For example:

.. code-block:: python

    class BookListSerializer(serializers.ListSerializer):

        def create(self, validated_data):
            books = [Book(**item) for item in validated_data]
            return Book.objects.bulk_create(books)

    class BookSerializer(serializers.Serializer):
        ...
        class Meta:
            list_serializer_class = BookListSerializer

Customizing multiple update
~~~~~~~~~~~~~~~~~~~~~~~~~~~
By default the :class:`ListSerializer` class does not support multiple updates. This is because the
behavior that should be expected for insertions and deletions is ambiguous.

To support multiple updates you'll need to do so explicitly. When writing your multiple update code
make sure to keep the following in mind:

- How do you determine which instance should be updated for each item in the list of data?
- How should insertions be handled? Are they invalid, or do they create new objects?
- How should removals be handled? Do they imply object deletion, or removing a relationship? Should
  they be silently ignored, or are they invalid?
- How should ordering be handled? Does changing the position of two items imply any state change or
  is it ignored?

You will need to add an explicit ``id`` field to the instance serializer. The default
implicitly-generated ``id`` field is marked as ``read_only``. This causes it to be removed on
updates. Once you declare it explicitly, it will be available in the list serializer's ``update``
method.

Here's an example of how you might choose to implement multiple updates:

.. code-block:: python

    class BookListSerializer(serializers.ListSerializer):

        def update(self, instance, validated_data):
            # Maps for id->instance and id->data item.
            book_mapping = {book.id: book for book in instance}
            data_mapping = {item['id']: item for item in validated_data}

            # Perform creations and updates.
            ret = []
            for book_id, data in data_mapping.items():
                book = book_mapping.get(book_id, None)
                if book is None:
                    ret.append(self.child.create(data))
                else:
                    ret.append(self.child.update(book, data))

            # Perform deletions.
            for book_id, book in book_mapping.items():
                if book_id not in data_mapping:
                    book.delete()

            return ret

    class BookSerializer(serializers.Serializer):
        # We need to identify elements in the list using their primary key,
        # so use a writable field here, rather than the default which would be read-only.
        id = serializers.IntegerField()

        ...
        id = serializers.IntegerField(required=False)

        class Meta:
            list_serializer_class = BookListSerializer

Customizing ListSerializer initialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When a serializer with ``many=True`` is instantiated, we need to determine which arguments and
keyword arguments should be passed to the ``.__init__()`` method for both the child
:class:`Serializer` class, and for the parent :class:`ListSerializer` class.

The default implementation is to pass all arguments to both classes, except for ``validators``, and
any custom keyword arguments, both of which are assumed to be intended for the child serializer
class.

Occasionally you might need to explicitly specify how the child and parent classes should be
instantiated when ``many=True`` is passed. You can do so by using the ``many_init`` class method.

.. code-block:: python

    @classmethod
    def many_init(cls, *args, **kwargs):
        # Instantiate the child serializer.
        kwargs['child'] = cls()
        # Instantiate the parent list serializer.
        return CustomListSerializer(*args, **kwargs)

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
