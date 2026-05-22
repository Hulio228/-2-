from django.db.models import Count, QuerySet
from django.utils import timezone


class CustomQuerySet(QuerySet):

    def annotate_comment_count(self):
        return (
            self.prefetch_related('comments_for_post')
            .annotate(comment_count=Count('comments_for_post'))
            .order_by('-pub_date', 'title')
        )

    def publish_filter(self):
        return (
            self.select_related('author', 'category', 'location')
            .filter(
                is_published=True,
                pub_date__lte=timezone.now(),
            )
        )

    def category_filter(self):
        return self.publish_filter().filter(category__is_published=True)

    def all_filter(self):
        return self.category_filter().annotate_comment_count()
