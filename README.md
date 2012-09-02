python-fipe
===========

A simple python API to access fipe vehicles indexes.
This API should provide a way for you to create your own copy of the data
available through fipe website or to query their data once in while.

You should **not** use or rely on this API to constantly load their server with
requests. And for that reason, performance will not be considered an issue.

More information about fipe, see their [website](http://www.fipe.org.br).

Current version: 0.1 (in development)


Requirements
------------

* requests
* lxml


Examples
--------

::
    >>> from fipe.vehicle import VehicleAPI
    >>> api = VehicleAPI()
    {0: 'Cars', 1: 'Motorbikes', 2: 'Trunks'}
    # it should be used as: api.VEHICLE_CAR, api.VEHICLE_MOTORBIKE
    # and api.VEHICLE_TRUNK

    # loading vehicle brands (using list, because it returns a generator):
    >>> brands = list(api.get_vehicle_brands(api.VEHICLE_CAR))
    >>> brands[0]
    VehicleBrand(pk='1', brand='Acura', vtype=1)

    # loading vehicle models from that brand:
    >>> models = list(api.get_vehicle_models(brands[0]))
    >>> models[0]
    VehicleModel(pk='038003-2', model='Integra GS 1.8', vbrand=VehicleBrand(
    pk='1', brand='Acura', vtype=0))

    # loading year options using that vehicle model:
    >>> years = list(api.get_vehicle_years(models[0]))
    >>> years[0]
    VehicleYear(pk='1855904', model='1992 Gasolina', vmodel=VehicleModel(
    pk ='038003-2', model='Integra GS 1.8', vbrand=VehicleBrand(pk='1', brand=
    'Acura', vtype=0)))

    # loading fipe data using the vehicle year reference:
    >>> api.get_vehicle_data(years[0])
    VehicleData(fipe_code='038003-2', reference='Setembro de 2012',
    average_value='R$ 15.138,00',
    query_date='domingo, 02 de setembro de 2012 0:14 ',
    vyear=VehicleYear(pk='1855904', model='1992 Gasolina',
    vmodel=VehicleModel(pk='038003-2', model='Integra GS 1.8',
    vbrand=VehicleBrand(pk='1', brand='Acura', vtype=0))))
    ...


This data flow should work as shown, but there's a bug when we make wrong
calls at some point and we should fetch some expected data to query their
database.
At the moment, the only workaround is restart the api calls from
api.get_vehicle_brands().


TODO & Bugs
-----------

* handle errors
* add tests
* add documentation
* packaging stuff
* handle when the form data is invalidated
