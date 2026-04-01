from django.db import migrations, models
from django.utils.text import slugify


def populate_post_slugs(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')

    for post in Post.objects.all().order_by('id'):
        if post.slug:
            continue

        base_slug = slugify(post.title) or 'post'
        slug = base_slug
        counter = 1

        while Post.objects.filter(slug=slug).exclude(pk=post.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        post.slug = slug
        post.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_category_alter_post_options_post_image_post_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
        migrations.RunPython(populate_post_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
