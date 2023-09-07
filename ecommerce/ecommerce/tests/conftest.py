import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

from .factories import (
    AttributeFactory,
    AttributeValueFactory,
    CategoryFactory,
    ProductFactory,
    ProductImageFactory,
    ProductLineAttributeValueFactory,
    ProductLineFactory,
    ProductTypeFactory,
)

register(AttributeFactory)
register(AttributeValueFactory)
register(CategoryFactory)
register(ProductFactory)
register(ProductLineFactory)
register(ProductImageFactory)
register(ProductTypeFactory)
register(ProductLineAttributeValueFactory)


@pytest.fixture
def api_client():
    return APIClient
