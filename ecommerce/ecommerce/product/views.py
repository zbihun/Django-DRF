from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Product, ProductImage, ProductLine
from .serializers import (
    CategorySerializer,
    ProductCategorySerializer,
    ProductSerializer,
)


class CategoryViewSet(viewsets.ViewSet):
    """
    A simple viewset for viewing all Categories
    """

    queryset = Category.objects.all().is_active()

    @extend_schema(responses=CategorySerializer)
    def list(self, request):
        serializer = CategorySerializer(self.queryset, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ViewSet):
    """
    A simple viewset for viewing all Products
    """

    queryset = Product.objects.is_active().all()
    lookup_field = "slug"

    def retrieve(self, request, slug=None):
        serializer = ProductSerializer(
            self.queryset.filter(slug=slug)
            .prefetch_related(
                Prefetch("attribute_values__attribute")
            )
            .prefetch_related("product_line__product_image")
            .prefetch_related("product_line__attribute_values__attribute"),
            many=True,
        )
        data = Response(serializer.data)
        return data

    @action(
        methods=["get"],
        detail=False,
        url_path=r"category/(?P<slug>[\w-]+)/all",
    )
    def list_product_by_category_slug(self, request, slug=None):
        """
        An endpoint to return products by category
        """
        serializer = ProductCategorySerializer(
            self.queryset.filter(category__slug=slug)
            .prefetch_related(
                Prefetch("product_line", queryset=ProductLine.objects.order_by("order"))
            )
            .prefetch_related(
                Prefetch(
                    "product_line__product_image",
                    queryset=ProductImage.objects.filter(order=1),
                ),
            ),
            many=True,
        )
        return Response(serializer.data)
