from io import BytesIO
import sys
import os

from PIL import Image
from django.conf import settings
from django.core.files.storage import default_storage as storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models import Q, signals
from django.utils.text import slugify

use_sites = hasattr(settings, "SITE_ID")

if use_sites:
    from django.contrib.sites.models import Site
    from django.contrib.sites.managers import CurrentSiteManager

config = {
    'shortcut icon': [16, 32, 48, 128, 192],
    'touch-icon': [192],
    'icon': [192],
    'apple-touch-icon': [57, 72, 114, 144, 180],
    'apple-touch-icon-precomposed': [57, 72, 76, 114, 120, 144, 152, 180],
}

config = getattr(settings, 'FAVICON_CONFIG', config)
if "shortcut icon" not in config or 32 not in config["shortcut icon"]:
    config.setdefault("shortcut_icon", []).append(32)


image_path = getattr(settings, "FAVICON_PATH", "favicon")

def get_image_path(instance, filename):
    return os.path.join(image_path, filename)

def pre_delete_image(sender, instance, **kwargs):
    instance.del_image()


class Favicon(models.Model):
    title = models.CharField(max_length=100)
    faviconImage = models.ImageField(upload_to=get_image_path)

    isFavicon = models.BooleanField(default=True)

    objects = models.Manager()
    on_site = objects

    if use_sites:
        site = models.ForeignKey(Site, related_name="favicon", on_delete=models.CASCADE, blank=True, null=True, default=settings.SITE_ID)

        on_site = CurrentSiteManager()

        def save(self, *args, **kwargs):
            self.site = Site.objects.get_current()
            return super(Favicon, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Favicon'
        verbose_name_plural = 'Favicons'

    def get_favicons(self, update=False, config_override=None):
        """
        Get all combinations of favicons as configured, creating mising ones.

        Pass update=True to force re-generation of existing icons.
        """
        # Use default config by default
        if config_override is None:
            config_override = config
        # Get all combinations of favicon rels and sizes from config
        query = Q()
        for rel in config_override:
            for size in config_override[rel]:
                query |= Q(rel=rel, size=size)

        # Get all existing favicons
        favicons = FaviconImg.objects.filter(faviconFK=self).filter(query)

        # Delete all favicon images to update all
        if update:
            favicons.delete()
            favicons = FaviconImg.objects.none()
            found = []
        else:
            favicons = favicons.all()
            found = [(f.rel, f.size) for f in favicons]

        # Check whether favicons are missing
        new_favicons = []
        for rel in config_override:
            for size in config_override[rel]:
                if not (rel, size) in found:
                    fav = FaviconImg(faviconFK=self, size=size, rel=rel)
                    fav.generate_image()
                    new_favicons.append(fav)
        if new_favicons:
            FaviconImg.objects.bulk_create(new_favicons, ignore_conflicts=True)

        return list(favicons) + new_favicons

    def __str__(self):
        return self.faviconImage.name

    def get_absolute_url(self):
        return self.faviconImage.name

    def del_image(self):
        self.faviconImage.delete()

    def as_html(self, update=False):
        """Return <link> html tags for this favicon set."""
        html = ''
        for favicon in self.get_favicons(update=update):
            html += favicon.as_html()
        return html

    def save(self, *args, **kwargs):
        if self.isFavicon:
            Favicon.on_site.exclude(pk=self.pk).update(isFavicon=False)

        super().save(*args, **kwargs)

        if self.faviconImage:
            self.get_favicons(update=True)


class FaviconImg(models.Model):
    faviconFK = models.ForeignKey(Favicon, on_delete=models.CASCADE)
    size = models.IntegerField()
    rel = models.CharField(max_length=250, null=True)
    faviconImage = models.ImageField(upload_to=get_image_path)

    def as_html(self):
        """Return a <link> tag forthis favicon image."""
        return f'<link rel="{self.rel}" sizes="{self.size}x{self.size}" href="{self.faviconImage.url}"/>'

    def generate_image(self):
        tmp = Image.open(storage.open(self.faviconFK.faviconImage.name))
        tmp.thumbnail((self.size, self.size), Image.LANCZOS)

        tmp_io = BytesIO()
        tmp.save(tmp_io, format='PNG')
        file_name = f"{slugify(self.faviconFK.title)}-{self.size}s.png"
        tmp_file = InMemoryUploadedFile(tmp_io, None, file_name, 'image/png', sys.getsizeof(tmp_io), None)

        self.faviconImage = tmp_file

    def del_image(self):
        self.faviconImage.delete()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["faviconFK", "size", "rel"], name="favicon_size_rel_unique")]


signals.pre_delete.connect(pre_delete_image, sender=Favicon)
signals.pre_delete.connect(pre_delete_image, sender=FaviconImg)
