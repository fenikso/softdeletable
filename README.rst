Softdeletable
=============

Softdeletable is a Django app that provides soft delete functionality for your models. Instead of permanently deleting objects from the database, it marks them as deleted, allowing you to restore them later if needed.

Features
--------

- Soft delete objects by marking them as deleted without removing them from the database.
- Restore soft-deleted objects.
- Query for available (non-deleted) and soft-deleted objects.
- Integration with Django admin for managing soft-deleted objects.
- Support for related objects soft deletion.

Installation
------------

1. Install the package using pip::

    pip install softdeletable

2. Add `softdeletable` to your `INSTALLED_APPS` in your Django settings::

    INSTALLED_APPS = [
        ...
        'softdeletable',
        ...
    ]

3. Run the migrations to create the necessary database tables::

    python manage.py migrate

Usage
-----

Models
~~~~~~

To use soft delete functionality, inherit your models from `SoftDeletableModel`::

    from softdeletable.models import SoftDeletableModel

    class MyModel(SoftDeletableModel):
        name = models.CharField(max_length=255)
        ...

Querying
~~~~~~~~

Use the custom manager methods to query for available and soft-deleted objects::

    # Get all objects (including soft-deleted)
    all_objects = MyModel.objects.all()

    # Get all available objects
    available_objects = MyModel.objects.available()

    # Get all soft-deleted objects
    softdeleted_objects = MyModel.objects.softdeleted()

Soft Deleting and Restoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Soft delete an object::

    obj = MyModel.objects.get(id=1)
    obj.softdelete()

Restore a soft-deleted object::

    obj = MyModel.objects.get(id=1)
    obj.restore()

Admin Integration
~~~~~~~~~~~~~~~~~

To integrate soft-delete functionality into the Django admin, use the provided admin classes::

    from django.contrib import admin
    from softdeletable.admin import AvailableAdmin, SoftdeletedAdmin
    from .models import MyModel

    class MyModelAvailableAdmin(AvailableAdmin):
        # Shown only available objects

        @staticmethod
        def get_model():
            return MyModel

    class MyModelSoftdeletedAdmin(SoftdeletedAdmin):
        # Shown only soft-deleted objects

        @staticmethod
        def get_model():
            return MyModel

    admin.site.register(MyModel, MyModelAvailableAdmin)
    admin.site.register(MyModel, MyModelSoftdeletedAdmin)


If you need more than one admin class for a specific model, you must use proxy models::

    class MyModelAvailable(MyModel):
        class Meta:
            proxy = True

    class MyModelSoftdeleted(MyModel):
        class Meta:
            proxy = True

    admin.site.register(MyModel

Running Tests
-------------

To run the tests, use the following command::

    python manage.py test softdeletable

License
-------

This project is licensed under the MIT License.

Contributing
------------

Contributions are welcome! Please open an issue or submit a pull request.

Contact
-------

For any questions or inquiries, please contact the repository owner.
