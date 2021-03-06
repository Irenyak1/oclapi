from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from djangotoolbox.fields import ListField
from collection.models import Collection
from oclapi.models import BaseResourceModel, ACCESS_TYPE_NONE, ACCESS_TYPE_EDIT, ACCESS_TYPE_VIEW
from sources.models import Source
from users.models import UserProfile

ORG_OBJECT_TYPE = 'Organization'


class Organization(BaseResourceModel):
    name = models.TextField()
    company = models.TextField(null=True, blank=True)
    website = models.TextField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    members = ListField()

    def delete(self, **kwargs):
        collections = Collection.objects.filter(parent_id=self.id)
        for collection in collections:
            collection.delete()

        sources = Source.objects.filter(parent_id=self.id)
        for source in sources:
            source.delete()

        users = UserProfile.objects.filter(organizations__contains=self.id)
        for user in users:
            user.organizations.remove(self.id)
            user.save()

        super(Organization, self).delete()

    def __unicode__(self):
        return self.mnemonic

    @classmethod
    def resource_type(cls):
        return ORG_OBJECT_TYPE

    @property
    def num_members(self):
        return len(self.members)

    @property
    def public_collections(self):
        return Collection.objects.filter(~Q(public_access=ACCESS_TYPE_NONE), parent_id=self.id).count()

    @property
    def public_sources(self):
        return Source.objects.filter(~Q(public_access=ACCESS_TYPE_NONE), parent_id=self.id).count()

    @property
    def public_can_view(self):
        return self.public_access in [ACCESS_TYPE_EDIT, ACCESS_TYPE_VIEW]

    @property
    def members_url(self):
        return reverse('organization-members', kwargs={'org': self.mnemonic})

    @property
    def sources_url(self):
        return reverse('source-list', kwargs={'org': self.mnemonic})

    @property
    def collections_url(self):
        return reverse('collection-list', kwargs={'org': self.mnemonic})

    @property
    def num_stars(self):
        return 0

    @staticmethod
    def get_url_kwarg():
        return 'org'


admin.site.register(Organization)
