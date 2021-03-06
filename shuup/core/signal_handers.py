# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.

# extends SQLite with necessary functions
from django.db.backends.signals import connection_created
from django.db.models.signals import m2m_changed, post_save

from shuup.core.models import Product, ShopProduct, Tax, TaxClass
from shuup.core.utils.context_cache import (
    bump_product_signal_handler, bump_shop_product_signal_handler
)
from shuup.core.utils.db import extend_sqlite_functions
from shuup.core.utils.price_cache import (
    bump_all_price_caches, bump_prices_for_product,
    bump_prices_for_shop_product
)


def handle_post_save_bump_all_prices_caches(sender, instance, **kwargs):
    # bump all the prices for all the shops, as it is impossible to know
    # from which shop things have changed
    bump_all_price_caches()


def handle_product_post_save(sender, instance, **kwargs):
    bump_product_signal_handler(sender, instance, **kwargs)
    bump_prices_for_product(instance)


def handle_shop_product_post_save(sender, instance, **kwargs):
    bump_shop_product_signal_handler(sender, instance, **kwargs)
    bump_prices_for_shop_product(instance)


# connect signals to bump caches on Product and ShopProduct change
m2m_changed.connect(
    handle_shop_product_post_save,
    sender=ShopProduct.categories.through,
    dispatch_uid="shop_product:change_categories"
)
post_save.connect(
    handle_product_post_save,
    sender=Product,
    dispatch_uid="product:bump_product_cache"
)
post_save.connect(
    handle_shop_product_post_save,
    sender=ShopProduct,
    dispatch_uid="shop_product:bump_shop_product_cache"
)

# connect signals to bump price caches on Tax and TaxClass change
post_save.connect(handle_post_save_bump_all_prices_caches, sender=Tax, dispatch_uid="tax_class:bump_prices_cache")
post_save.connect(handle_post_save_bump_all_prices_caches, sender=TaxClass, dispatch_uid="tax_class:bump_prices_cache")

connection_created.connect(extend_sqlite_functions)
