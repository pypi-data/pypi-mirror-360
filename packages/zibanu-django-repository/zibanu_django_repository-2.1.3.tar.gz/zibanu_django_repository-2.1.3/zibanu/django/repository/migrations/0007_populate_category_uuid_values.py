# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS.
#  Copyright ©. 2019 - 2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS.
#  Copyright ©. 2019 - 2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         31/03/25
# Project:      Zibanu Django
# Module Name:  0007_populate_category_uuid_values
# Description:
# ****************************************************************
import uuid
from django.db import migrations, models


def gen_uuid(apps, schema_editor):
    Category = apps.get_model('zb_repository', 'category')
    for category in Category.objects.all():
        category.uuid = uuid.uuid4()
        category.save(update_fields=['uuid'])



class Migration(migrations.Migration):
    dependencies = [
        ("zb_repository", "0006_category_uuid"),
    ]

    operations = [
        migrations.RunPython(gen_uuid),
        migrations.AlterField(
            model_name="category",
            name="uuid",
            field=models.UUIDField(editable=False, unique=True, null=False, blank=False),
        )
    ]