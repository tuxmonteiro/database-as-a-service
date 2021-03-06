# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
import simple_audit
from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from util.models import BaseModel


CACHE_MISS = object()
LOG = logging.getLogger(__name__)


class Configuration(BaseModel):

    name = models.CharField(verbose_name=_("Configuration name"), max_length=100, unique=True)
    value = models.CharField(verbose_name=_("Configuration value"), max_length=255)

    def clear_cache(self):
        key = self.get_cache_key(self.name)
        cache.delete(key)
        # cache.clear()

    @classmethod
    def get_cache_key(cls, configuration_name):
        return 'cfg:%s' % configuration_name

    @classmethod
    def get_by_name_as_list(cls, name, token=','):
        """returns a list splited by name for the given name"""
        config = Configuration.get_by_name(name) or []
        if config:
            return [item.strip() for item in config.split(token)]
        else:
            return config

    @classmethod
    def get_by_name_as_int(cls, name):
        """returns variable as int"""
        try:
            return int(Configuration.get_by_name(name))
        except:
            return None

    @classmethod
    def get_by_name(cls, name):
        key = cls.get_cache_key(name)
        value = cache.get(key, CACHE_MISS)
        if value is CACHE_MISS:
            value = Configuration.__get_by_name(name)
            cache.set(key, value)
        return value

    @classmethod
    def __get_by_name(cls, name):
        try:
            value = Configuration.objects.get(name=name).value
            LOG.debug("Configuration '%s': '%s'", name, value)
            return value
        except Configuration.DoesNotExist:
            LOG.warning("configuration %s not found" % name)
            return None
        except Exception, e:
            LOG.warning("ops.. could not retrieve configuration value for %s: %s" % (name, e))
            return None


@receiver([post_save, post_delete], sender=Configuration)
def clear_configuration_cache(sender, **kwargs):
    configuration = kwargs.get("instance")
    LOG.info('Clearing configuration for name=%s', configuration.name)
    configuration.clear_cache()


simple_audit.register(Configuration)
