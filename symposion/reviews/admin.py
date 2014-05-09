from django.contrib import admin

from symposion.reviews.models import NotificationTemplate, Review, ProposalResult

admin.site.register(Review,
        list_display = ['proposal', 'vote', 'user'],
        list_filter = ['vote',],
        date_heirarchy='submitted_at',
        )
admin.site.register(NotificationTemplate)
admin.site.register(ProposalResult,
        list_display=["proposal", "status"],
        list_filter=["status"],
)
