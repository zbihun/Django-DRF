from typing import Collection, Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.query import QuerySet
from mptt.models import MPTTModel, TreeForeignKey

from .fields import OrderField


class ActiveQuerySet(models.QuerySet):
    def isactive(self):
        return self.filter(is_active=True)


class Category(MPTTModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=255)
    parent = TreeForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    is_active = models.BooleanField(default=False)

    objects = ActiveQuerySet().as_manager()

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=False)

    objects = ActiveQuerySet().as_manager()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255)
    is_digital = models.BooleanField(default=False)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = TreeForeignKey(
        "Category", on_delete=models.SET_NULL, null=True, blank=True
    )
    is_active = models.BooleanField(default=False)
    product_type = models.ForeignKey("ProductType", on_delete=models.PROTECT)

    objects = ActiveQuerySet().as_manager()

    def __str__(self):
        return self.name


class Attribute(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    attribute_value = models.CharField(max_length=100)
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name="attribute_value"
    )

    def __str__(self):
        return f"{self.attribute.name} - {self.attribute_value}"


class ProductType(models.Model):
    name = models.CharField(max_length=100)
    attribute = models.ManyToManyField(
        Attribute,
        through="ProductTypeAttribute",
        related_name="product_type_attribute",
    )

    def __str__(self):
        return self.name


class ProductTypeAttribute(models.Model):
    product_type = models.ForeignKey(
        ProductType, on_delete=models.CASCADE, related_name="product_type_attribute_pt"
    )
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name="product_type_attribute_at"
    )

    class Meta:
        unique_together = ("product_type", "attribute")


class ProductLine(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=5)
    sku = models.CharField(max_length=100)
    stock_qty = models.IntegerField()
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_line"
    )
    is_active = models.BooleanField(default=False)
    order = OrderField(
        unique_for_field="product",
        blank=True,
    )
    attribute_values = models.ManyToManyField(
        AttributeValue,
        through="ProductLineAttributeValue",
        related_name="product_line_attribute_value",
    )

    objects = ActiveQuerySet().as_manager()

    def clean(self, exclude: Collection[str] | None = ...) -> None:
        qs = ProductLine.objects.filter(product=self.product)
        for obj in qs:
            if self.id != obj.id and self.order == obj.order:
                raise ValidationError("Duplicate value for order")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(ProductLine, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.sku)


class ProductLineAttributeValue(models.Model):
    attribute_value = models.ForeignKey(
        AttributeValue,
        on_delete=models.CASCADE,
        related_name="product_attribute_value_av",
    )
    product_line = models.ForeignKey(
        ProductLine,
        on_delete=models.CASCADE,
        related_name="product_attribute_value_pl",
    )

    class Meta:
        unique_together = ("attribute_value", "product_line")

    def clean(self) -> None:
        qs = (
            ProductLineAttributeValue.objects.filter(
                attribute_value=self.attribute_value
            )
            .filter(product_line=self.product_line)
            .exists()
        )

        if not qs:
            iqs = Attribute.objects.filter(
                attribute_value__product_line_attribute_value=self.product_line
            ).values_list("pk", flat=True)

            if self.attribute_value.attribute.id in list(iqs):
                raise ValidationError("Duplicate value exists")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(ProductLineAttributeValue, self).save(*args, **kwargs)


class ProductImage(models.Model):
    alternative_text = models.CharField(max_length=100)
    image = models.ImageField(upload_to=None, default="test.jpg")
    product_line = models.ForeignKey(
        ProductLine, on_delete=models.CASCADE, related_name="product_image"
    )
    order = OrderField(
        unique_for_field="product_line",
        blank=True,
    )

    def clean(self):
        qs = ProductImage.objects.filter(product_line=self.product_line)
        for obj in qs:
            if self.id != obj.id and self.order == obj.order:
                raise ValidationError("Duplicate value for order")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(ProductImage, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.image)
