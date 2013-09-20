# -*- coding:utf-8 -*-
from django.utils import unittest
from django.test.client import Client
from django.test import TestCase
from django.utils import simplejson
from django.test.client import RequestFactory
from django.db import IntegrityError

from .models import Engine, EngineType, Node, Environment, Instance

from business.models import Product, Plan

from engine.factory import EngineFactory

class EngineTestCase(TestCase):
    """
    Tests Engine and EngineType
    """

    fixtures = ['config_business.yaml']
    
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.new_engine_type = EngineType.objects.create(name="Test")
        self.environment = Environment.objects.get(id=1)

    def tearDown(self):
        self.new_engine_type.delete()

    def test_create_engine_type(self):

        engine_type = EngineType.objects.create(name="John...1..2..3..")

        self.assertTrue(engine_type.id)

    def test_error_duplicate_engine_type(self):

        self.assertRaises(IntegrityError, EngineType.objects.create, name="Test")

    def test_create_engine_in_bd(self):

        engine_type = EngineType.objects.create(name="Maria")

        self.assertTrue(engine_type.id)

        engine = Engine.objects.create(version="1.2.3", engine_type=engine_type)

        self.assertTrue(engine.id)

    