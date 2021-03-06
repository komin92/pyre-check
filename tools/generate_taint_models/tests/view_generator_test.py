# Copyright (c) 2016-present, Facebook, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict


import unittest
from typing import Callable, Iterable
from unittest.mock import patch

from .. import model_generator, view_generator
from ..model import Model


class ViewGeneratorTest(unittest.TestCase):
    def test_view_generator(self) -> None:
        class Url:
            def __init__(self, value: int) -> None:
                self.value = value

            def callback(self) -> int:
                return self.value

        class Resolver:
            pass

        class FirstUrls(Resolver):
            url_patterns = [Url(1), Url(2), Url(3)]

        class SecondUrls(Resolver):
            url_patterns = [FirstUrls(), Url(4), Url(5), Url(6)]

        class Urls:
            urlpatterns = [SecondUrls(), Url(7)]

        with patch(f"{view_generator.__name__}.import_module", return_value=Urls):
            views = view_generator.get_all_views(
                view_generator.DjangoUrls(
                    urls_module="urls", url_pattern_type=Url, url_resolver_type=Resolver
                )
            )
            values = [view() for view in views]
            self.assertEqual(values, [1, 2, 3, 4, 5, 6, 7])

        with patch.object(view_generator, "Configuration") as configuration:
            configuration.urls_module = None
            configuration.url_resolver_type = Resolver
            configuration.url_pattern_type = Url
            self.assertEqual(view_generator.django_urls_from_configuration(), None)
            configuration.urls_module = "urls"
            self.assertEqual(
                view_generator.django_urls_from_configuration(),
                view_generator.DjangoUrls(
                    urls_module="urls", url_resolver_type=Resolver, url_pattern_type=Url
                ),
            )
