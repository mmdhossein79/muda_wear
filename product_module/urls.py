def get_absolute_url(self):
    return reverse('product-detail', args=[self.slug])


def save(self, *args, **kwargs):
    # self.slug = slugify(self.title)
    super().save(*args, **kwargs)


def __str__(self):
    return f"{self.title} ({self.price})"


class Meta:
    verbose_name = 'محصول'
    verbose_name_plural = 'محصولات'


from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product-list'),
    path('cat/<cat>', views.ProductListView.as_view(), name='product-categories-list'),
    path('brand/<brand>', views.ProductListView.as_view(), name='product-list-by-brands'),
    path('product-favorite', views.AddProductFavorite.as_view(), name='product-favorite'),
    path('<slug:slug>', views.ProductDetailView.as_view(), name='product-detail'),
]
