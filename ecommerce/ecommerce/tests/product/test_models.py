import pytest
from django.core.exceptions import ValidationError

pytestmark = pytest.mark.django_db


class TestCategoryModel:
    def test_str_method(self, category_factory):
        data = category_factory(name="test_cat")
        assert data.__str__() == "test_cat"


class TestBrandModel:
    def test_str_method(self, brand_factory):
        data = brand_factory(name="test_brand")
        assert data.__str__() == "test_brand"


class TestProductModel:
    def test_str_method(self, product_factory):
        data = product_factory(name="test_product")
        assert data.__str__() == "test_product"


class TestProductLineModel:
    def test_str_method(self, product_line_factory):
        data = product_line_factory(sku="12345")
        assert data.__str__() == "12345"

    def test_duplicate_order_values(self, product_line_factory, product_factory):
        product = product_factory()
        product_line_factory(product=product, order=1)
        with pytest.raises(ValidationError):
            product_line_factory(product=product, order=1).clean()
