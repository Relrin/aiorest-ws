.. _aiorest-ws-relations:

Serializer relations
====================

.. currentmodule:: aiorest_ws.db.orm.relations

Relational fields are used to represent model relationships. They can be applied to foreign key,
many-to-many and one-to-one relationships, as well as to reverse relationships, and custom
relationships such as :class:`GenericForeignKey` of Django.

*Note*: The relational fields are declared in ``relations.py``, but by convention you should import
them from the ``serializers`` module, using from ``aiorest-ws.db.orm.django import serializers`` or
``aiorest-ws.db.orm.sqlalchemy import serializers`` and refer to fields as ``serializers.<FieldName>``.

Inspecting relationships
------------------------
When using the :class:`ModelSerializer` class, serializer fields and relationships will be
automatically generated for you. Inspecting these automatically generated fields can be a useful
tool for determining how to customize the relationship style.

To do so, open the shell, then import the serializer class, instantiate it, and print the object
representation…

>>> from myapp.serializers import AccountSerializer
>>> serializer = AccountSerializer()
>>> print(repr(serializer))
AccountSerializer():
    id = IntegerField(label='ID', read_only=True)
    name = CharField(allow_blank=True, max_length=100, required=False)
    owner = PrimaryKeyRelatedField(queryset=User.objects.all())

Serializer relation fields
--------------------------
In order to explain the various types of relational fields, we'll use a couple of simple models
for our examples. Our models will be for music albums, and the tracks listed on each album, based
on the Django models.

.. code-block:: python

    class Album(models.Model):
        album_name = models.CharField(max_length=100)
        artist = models.CharField(max_length=100)

    class Track(models.Model):
        album = models.ForeignKey(Album, related_name='tracks', on_delete=models.CASCADE)
        order = models.IntegerField()
        title = models.CharField(max_length=100)
        duration = models.IntegerField()

        class Meta:
            unique_together = ('album', 'order')
            ordering = ['order']

        def __unicode__(self):
            return '%d: %s' % (self.order, self.title)

StringRelatedField
^^^^^^^^^^^^^^^^^^
:class:`StringRelatedField` may be used to represent the target of the relationship using its
``__unicode__`` method.

For example, the following serializer.

.. code-block:: python

    class AlbumSerializer(serializers.ModelSerializer):
        tracks = serializers.StringRelatedField(many=True)

        class Meta:
            model = Album
            fields = ('album_name', 'artist', 'tracks')

Would serialize to the following representation.

.. code-block:: python

    {
        'album_name': 'Things We Lost In The Fire',
        'artist': 'Low',
        'tracks': [
            '1: Sunflower',
            '2: Whitetail',
            '3: Dinosaur Act',
            ...
        ]
    }

This field is read only.

**Arguments**:

- ``many`` - If applied to a to-many relationship, you should set this argument to ``True``.

PrimaryKeyRelatedField
^^^^^^^^^^^^^^^^^^^^^^
:class:`PrimaryKeyRelatedField` may be used to represent the target of the relationship using its
primary key.

For example, the following serializer:

.. code-block:: python

    class AlbumSerializer(serializers.ModelSerializer):
        tracks = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

        class Meta:
            model = Album
            fields = ('album_name', 'artist', 'tracks')

Would serialize to a representation like this:

.. code-block:: python

    {
        'album_name': 'Undun',
        'artist': 'The Roots',
        'tracks': [
            89,
            90,
            91,
            ...
        ]
    }

By default this field is read-write, although you can change this behavior using the ``read_only``
flag.

**Arguments**:

- ``queryset`` - The queryset used for model instance lookups when validating the field input.
  Relationships must either set a queryset explicitly, or set ``read_only=True``.
- ``many`` - If applied to a to-many relationship, you should set this argument to ``True``.
- ``allow_null`` - If set to ``True``, the field will accept values of ``None`` or the empty string
  for nullable relationships. Defaults to ``False``.
- ``pk_field`` - Set to a field to control serialization/deserialization of the primary key's value.
  For example, ``pk_field=UUIDField(format='hex')`` would serialize a UUID primary key into its
  compact hex representation.

HyperlinkedRelatedField
^^^^^^^^^^^^^^^^^^^^^^^
:class:`HyperlinkedRelatedField` may be used to represent the target of the relationship using a
hyperlink.

For example, the following serializer:

.. code-block:: python

    class AlbumSerializer(serializers.ModelSerializer):
        tracks = serializers.HyperlinkedRelatedField(
            many=True,
            read_only=True,
            view_name='track-detail'
        )

        class Meta:
            model = Album
            fields = ('album_name', 'artist', 'tracks')

Would serialize to a representation like this:

.. code-block:: python

    {
        'album_name': 'Graceland',
        'artist': 'Paul Simon',
        'tracks': [
            'http://www.example.com/api/tracks/45/',
            'http://www.example.com/api/tracks/46/',
            'http://www.example.com/api/tracks/47/',
            ...
        ]
    }

By default this field is read-write, although you can change this behavior using the ``read_only``
flag.

*Note*: This field is designed for objects that map to a URL that accepts a single URL keyword
argument, as set using the ``lookup_field`` and ``lookup_url_kwarg`` arguments.

This is suitable for URLs that contain a single primary key or slug argument as part of the URL.

**Arguments**:

- ``view_name`` - The view name that should be used as the target of the relationship. If you're
  using the standard router classes this will be a string with the format ``<modelname>-detail``.
  **required**.
- ``queryset`` - The queryset used for model instance lookups when validating the field input.
  Relationships must either set a queryset explicitly, or set ``read_only=True``.
- ``many`` - If applied to a to-many relationship, you should set this argument to ``True``.
- ``allow_null`` - If set to ``True``, the field will accept values of ``None`` or the empty string
  for nullable relationships. Defaults to ``False``.
- ``lookup_field`` - The field on the target that should be used for the lookup. Should correspond
  to a URL keyword argument on the referenced view. Default is ``'pk'`` for Django or ``id`` for
  SQLAlchemy.
- ``lookup_url_kwarg`` - The name of the keyword argument defined in the URL conf that corresponds
  to the lookup field. Defaults to using the same value as ``lookup_field``.
- ``format`` - If using format suffixes, hyperlinked fields will use the same format suffix for the
  target unless overridden by using the ``format`` argument.

SlugRelatedField
^^^^^^^^^^^^^^^^
:class:`SlugRelatedField` may be used to represent the target of the relationship using a field on
the target.

For example, the following serializer:

.. code-block:: python

    class AlbumSerializer(serializers.ModelSerializer):
        tracks = serializers.SlugRelatedField(
            many=True,
            read_only=True,
            slug_field='title'
        )

        class Meta:
            model = Album
            fields = ('album_name', 'artist', 'tracks')

Would serialize to a representation like this:

.. code-block:: python

    {
        'album_name': 'Dear John',
        'artist': 'Loney Dear',
        'tracks': [
            'Airport Surroundings',
            'Everything Turns to You',
            'I Was Only Going Out',
            ...
        ]
    }

By default this field is read-write, although you can change this behavior using the ``read_only``
flag.

When using :class:`SlugRelatedField` as a read-write field, you will normally want to ensure that
the slug field corresponds to a model field with ``unique=True``.

**Arguments**:

- ``slug_field`` - The field on the target that should be used to represent it. This should be a
  field that uniquely identifies any given instance. For example, ``username``. **required**
- ``queryset`` - The queryset used for model instance lookups when validating the field input.
  Relationships must either set a queryset explicitly, or set ``read_only=True``.
- ``many`` - If applied to a to-many relationship, you should set this argument to ``True``.
- ``allow_null`` - If set to ``True``, the field will accept values of ``None`` or the empty string
  for nullable relationships. Defaults to ``False``.

HyperlinkedIdentityField
^^^^^^^^^^^^^^^^^^^^^^^^
This field can be applied as an identity relationship, such as the ``'url'`` field on a
:class:`HyperlinkedModelSerializer`. It can also be used for an attribute on the object. For
example, the following serializer:

.. code-block:: python

    class AlbumSerializer(serializers.HyperlinkedModelSerializer):
        track_listing = serializers.HyperlinkedIdentityField(view_name='track-list')

        class Meta:
            model = Album
            fields = ('album_name', 'artist', 'track_listing')

Would serialize to a representation like this:

.. code-block:: python

    {
        'album_name': 'The Eraser',
        'artist': 'Thom Yorke',
        'track_listing': 'http://www.example.com/api/track_list/12/',
    }

This field is always read-only.

**Arguments**:

- ``view_name`` - The view name that should be used as the target of the relationship. If you're
  using the standard router classes this will be a string with the format ``<model_name>-detail``.
  **required**.
- ``lookup_field`` - The field on the target that should be used for the lookup. Should correspond
  to a URL keyword argument on the referenced view. Default is ``'pk'`` for Django or ``id`` for
  SQLAlchemy.
- ``lookup_url_kwarg`` - The name of the keyword argument defined in the URL conf that corresponds
  to the lookup field. Defaults to using the same value as ``lookup_field``.
- ``format`` - If using format suffixes, hyperlinked fields will use the same format suffix for the
  target unless overridden by using the ``format`` argument.

Nested relationships
--------------------
Nested relationships can be expressed by using serializers as fields.

If the field is used to represent a to-many relationship, you should add the ``many=True`` flag to
the serializer field.

Example
^^^^^^^
For example, the following serializer:

.. code-block:: python

    class TrackSerializer(serializers.ModelSerializer):
        class Meta:
            model = Track
            fields = ('order', 'title', 'duration')

    class AlbumSerializer(serializers.ModelSerializer):
        tracks = TrackSerializer(many=True, read_only=True)

        class Meta:
            model = Album
            fields = ('album_name', 'artist', 'tracks')

Would serialize to a nested representation like this:

>>> album = Album.objects.create(album_name="The Grey Album", artist='Danger Mouse')
>>> Track.objects.create(album=album, order=1, title='Public Service Announcement', duration=245)
<Track: Track object>
>>> Track.objects.create(album=album, order=2, title='What More Can I Say', duration=264)
<Track: Track object>
>>> Track.objects.create(album=album, order=3, title='Encore', duration=159)
<Track: Track object>
>>> serializer = AlbumSerializer(instance=album)
>>> serializer.data
{
    'album_name': 'The Grey Album',
    'artist': 'Danger Mouse',
    'tracks': [
        {'order': 1, 'title': 'Public Service Announcement', 'duration': 245},
        {'order': 2, 'title': 'What More Can I Say', 'duration': 264},
        {'order': 3, 'title': 'Encore', 'duration': 159},
        ...
    ],
}

Writable nested serializers
^^^^^^^^^^^^^^^^^^^^^^^^^^^
By default nested serializers are read-only. If you want to support write-operations to a nested
serializer field you'll need to create ``create()`` and/or ``update()`` methods in order to
explicitly specify how the child relationships should be saved.

.. code-block:: python

    class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ('order', 'title', 'duration')

    class AlbumSerializer(serializers.ModelSerializer):
        tracks = TrackSerializer(many=True)

        class Meta:
            model = Album
            fields = ('album_name', 'artist', 'tracks')

        def create(self, validated_data):
            tracks_data = validated_data.pop('tracks')
            album = Album.objects.create(**validated_data)
            for track_data in tracks_data:
                Track.objects.create(album=album, **track_data)
            return album

>>> data = {
    'album_name': 'The Grey Album',
    'artist': 'Danger Mouse',
    'tracks': [
        {'order': 1, 'title': 'Public Service Announcement', 'duration': 245},
        {'order': 2, 'title': 'What More Can I Say', 'duration': 264},
        {'order': 3, 'title': 'Encore', 'duration': 159},
    ],
}
>>> serializer = AlbumSerializer(data=data)
>>> serializer.is_valid()
True
>>> serializer.save()
<Album: Album object>

Custom relational fields
------------------------
In rare cases where none of the existing relational styles fit the representation you need,
you can implement a completely custom relational field, that describes exactly how the output
representation should be generated from the model instance.

To implement a custom relational field, you should override :class:`RelatedField`, and implement
the ``.to_representation(self, value)`` method. This method takes the target of the field as the
``value`` argument, and should return the representation that should be used to serialize the target.
The ``value`` argument will typically be a model instance.

If you want to implement a read-write relational field, you must also implement the
``.to_internal_value(self, data)`` method.

To provide a dynamic queryset based on the ``context``, you can also override ``.get_queryset(self)``
instead of specifying ``.queryset`` on the class or when initializing the field.

Example
^^^^^^^
For example, we could define a relational field to serialize a track to a custom string
representation, using its ordering, title, and duration.

.. code-block:: python

    import time

    class TrackListingField(serializers.RelatedField):
        def to_representation(self, value):
            duration = time.strftime('%M:%S', time.gmtime(value.duration))
            return 'Track %d: %s (%s)' % (value.order, value.name, duration)

    class AlbumSerializer(serializers.ModelSerializer):
        tracks = TrackListingField(many=True)

        class Meta:
            model = Album
            fields = ('album_name', 'artist', 'tracks')

This custom field would then serialize to the following representation.

.. code-block:: python

    {
        'album_name': 'Sometimes I Wish We Were an Eagle',
        'artist': 'Bill Callahan',
        'tracks': [
            'Track 1: Jim Cain (04:39)',
            'Track 2: Eid Ma Clack Shaw (04:19)',
            'Track 3: The Wind and the Dove (04:34)',
            ...
        ]
    }


Custom hyperlinked fields
-------------------------
In some cases you may need to customize the behavior of a hyperlinked field, in order to represent
URLs that require more than a single lookup field.

You can achieve this by overriding :class:`HyperlinkedRelatedField`. There are two methods that may
be overridden:

.. code-block:: python

    get_url(self, obj, view_name, request, format)

The ``get_url`` method is used to map the object instance to its URL representation.

May raise a ``NoReverseMatch`` if the ``view_name`` and ``lookup_field`` attributes are not
configured to correctly match the URL conf.

.. code-block:: python

    get_object(self, queryset, view_name, view_args, view_kwargs)

If you want to support a writable hyperlinked field then you'll also want to override ``get_object``,
in order to map incoming URLs back to the object they represent. For read-only hyperlinked fields
there is no need to override this method.

The return value of this method should the object that corresponds to the matched URL conf arguments.

May raise an ``ObjectDoesNotExist`` exception.

Example
^^^^^^^
Say we have a URL for a customer object that takes two keyword arguments, like so:

.. code-block:: python

    /api/<organization_slug>/customers/<customer_pk>/

This cannot be represented with the default implementation, which accepts only a single lookup
field.

In this case we'd need to override :class:`HyperlinkedRelatedField` to get the behavior we want:

.. code-block:: python

    from aiorest_ws.db.orm.django import serializers
    from aiorest_ws.url.utils import reverse

    class CustomerHyperlink(serializers.HyperlinkedRelatedField):
        # We define these as class attributes, so we don't need to pass them as arguments.
        view_name = 'customer-detail'
        queryset = Customer.objects.all()

        def get_url(self, obj, view_name, request, format):
            relative = self.context.get('relative', False)
            args = tuple(map(str, [obj.organization.slug, obj.pk])
            return reverse(view_name, args=args, relative=relative)

        def get_object(self, view_name, view_args, view_kwargs):
            lookup_kwargs = {
               'organization__slug': view_kwargs['organization_slug'],
               'pk': view_kwargs['customer_pk']
            }
            return self.get_queryset().get(**lookup_kwargs)

Note that if you wanted to use this style together with the generic views then you'd also need to
override ``.get_object`` on the view in order to get the correct lookup behavior.

Generally we recommend a flat style for API representations where possible, but the nested URL
style can also be reasonable when used in moderation.
