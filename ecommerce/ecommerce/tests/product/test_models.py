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
    def test_str_method(self, product_line_factory, attribute_value_factory):
        attr = attribute_value_factory(attribute_value="test")
        obj = product_line_factory.create(sku="12345", attribute_values=(attr,))
        assert obj.__str__() == "12345"

    def test_duplicate_order_values(self, product_line_factory, product_factory):
        product = product_factory()
        product_line_factory(product=product, order=1)
        with pytest.raises(ValidationError):
            product_line_factory(product=product, order=1).clean()


class TestProductImageModel:
    def test_str_method(self, product_image_factory):
        data = product_image_factory(image="test_image.jpg")
        assert data.__str__() == "test_image.jpg"


class TestProductTypeModel:
    def test_str_method(self, product_type_factory, attribute_factory):
        test = attribute_factory(name="test")
        obj = product_type_factory.create(name="test_type", attribute=(test,))
        assert obj.__str__() == "test_type"


class TestAttributeModel:
    def test_str_method(self, attribute_factory):
        obj = attribute_factory(name="test_attribute")
        assert obj.__str__() == "test_attribute"


class TestAttributeValueModel:
    def test_str_method(self, attribute_value_factory, attribute_factory):
        obj_a = attribute_factory(name="test_attribute")
        obj_b = attribute_value_factory(attribute_value="test_value", attribute=obj_a)
        assert obj_b.__str__() == "test_attribute - test_value"
