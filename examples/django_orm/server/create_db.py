# -*- coding: utf-8 -*-
from app.db import Manufacturer, Car

from django.db import connections


if __name__ == '__main__':
    # Create tables in memory
    conn = connections['default']
    with conn.schema_editor() as editor:
        editor.create_model(Manufacturer)
        editor.create_model(Car)

    # Initialize the database
    data = {
        'Audi': ['A8', 'Q5', 'TT'],
        'BMW': ['M3', 'i8'],
        'Mercedes-Benz': ['C43 AMG W202', 'C450 AMG 4MATIC']
    }

    for name, models in data.items():
        manufacturer = Manufacturer.objects.create(name=name)

        for model in models:
            Car.objects.create(name=model, manufacturer=manufacturer)
