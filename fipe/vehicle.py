# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2012 - George Y. Kussumoto <georgeyk.dev@gmail.com>
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
##

from collections import namedtuple

import lxml.html
import requests


VehicleType = namedtuple('VehicleType', ['pk', 'name'])
VehicleBrand = namedtuple('VehicleBrand', ['pk', 'brand', 'vtype'])
VehicleModel = namedtuple('VehicleModel', ['pk', 'model', 'vbrand'])
VehicleYear = namedtuple('VehicleYear', ['pk', 'model', 'vmodel'])
VehicleData = namedtuple('VehicleData', ['fipe_code', 'reference',
                                         'average_value', 'query_date',
                                         'vyear'])

_translate = dict(lblReferencia='reference',
                  lblCodFipe='fipe_code',
                  lblValor='average_value',
                  lblData='query_date')


#TODO: Handle errors, improve api

class VehicleAPI(object):
    BASE_URL = 'http://www.fipe.org.br/web/indices/veiculos/default.aspx'

    (VEHICLE_CAR,
     VEHICLE_MOTORBIKE,
     VEHICLE_TRUNK) = range(3)

    TYPE_DESCRIPTION = {VEHICLE_CAR: 'Cars',
                        VEHICLE_MOTORBIKE: 'Motorbikes',
                        VEHICLE_TRUNK: 'Trunks'}

    TYPE_PARAMS = {VEHICLE_CAR: dict(p=51),
                   VEHICLE_MOTORBIKE: dict(p=52, v='m'),
                   VEHICLE_TRUNK: dict(p=53, v='c')}

    def __init__(self):
        self._cache_request_data = {}

    #
    # Private API
    #

    def _get_vehicle_params(self, vehicle_type):
        for key, value in VehicleAPI.TYPE_DESCRIPTION.items():
            if key == vehicle_type or value == vehicle_type:
                return VehicleAPI.TYPE_PARAMS[key]

    def _update_cache_request_data(self, data):
        root = lxml.html.fromstring(data)
        for i in root.cssselect('#form1 input[type="hidden"]'):
            self._cache_request_data[i.name] = i.value

    def _request_data(self, vehicle_type, data):
        params = self._get_vehicle_params(vehicle_type)
        if params is None:
            print 'vehicle type not found'
            return

        data.update(self._cache_request_data)
        response = requests.post(VehicleAPI.BASE_URL, params=params, data=data)
        if not response.ok:
            print 'request error'
            return

        data = response.content
        self._update_cache_request_data(data)
        return data

    def _css_select_from_data(self, selector, data, skip_match=''):
        root = lxml.html.fromstring(data)
        results = root.cssselect(selector)
        for item in results:
            if skip_match and skip_match in item.text:
                continue

            yield item

    #
    # Public API
    #

    def clear_cache(self):
        self._cache_request_data.clear()

    def get_vehicle_types(self):
        return self.TYPE_DESCRIPTION

    def get_vehicle_brands(self, vehicle_type):
        request_data = {'ScriptManager1': 'UdtMarca|ddlMarca', 'ddlMarca': ''}
        self.clear_cache()
        data = self._request_data(vehicle_type, request_data)
        if not data:
            return

        items = self._css_select_from_data('select[name="ddlMarca"] option',
                                           data, skip_match='Selecione ')
        for item in items:
            yield VehicleBrand(pk=item.values()[0], brand=item.text,
                               vtype=vehicle_type)

    def get_vehicle_models(self, brand):
        request_data = {'ScriptManager1': 'UdtMarca|ddlMarca',
                        'ddlMarca': brand.pk, 'ddlModelo': '0'}
        data = self._request_data(brand.vtype, request_data)
        if not data:
            return

        items = self._css_select_from_data('select[name="ddlModelo"] option',
                                           data, skip_match='Selecione ')
        for item in items:
            yield VehicleModel(pk=item.values()[0], model=item.text,
                               vbrand=brand)

    def get_vehicle_years(self, model):
        request_data = {'ScriptManager1': 'updModelo|ddlModelo',
                        'ddlMarca': model.vbrand.pk, 'ddlModelo': model.pk, }
        data = self._request_data(model.vbrand.vtype, request_data)
        if not data:
            return

        items = self._css_select_from_data('select[name="ddlAnoValor"] option',
                                           data, skip_match='Selecione ')
        for item in items:
            yield VehicleYear(pk=item.values()[0], model=item.text,
                              vmodel=model)

    def get_vehicle_data(self, year):
        request_data = {'ScriptManager1': 'updAnoValor|ddlAnoValor',
                        'ddlMarca': year.vmodel.vbrand.pk,
                        'ddlModelo': year.vmodel.pk, 'ddlAnoValor': year.pk}
        data = self._request_data(year.vmodel.vbrand.vtype, request_data)
        if not data:
            return

        items = self._css_select_from_data('#pnlResultado table td span', data)
        tmp = dict()
        for item in items:
            label = item.values()[0]
            if _translate.has_key(label):
                tmp[_translate[label]] = item.text
        tmp['vyear'] = year
        return VehicleData(**tmp)
