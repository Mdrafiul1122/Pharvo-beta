import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0004_inventorytransaction"),
        ("sales", "0002_convert_product_to_medicine"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="saleitem",
            name="product",
        ),
        migrations.AddField(
            model_name="saleitem",
            name="medicine",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="sale_items",
                to="inventory.medicine",
            ),
        ),
        migrations.AlterField(
            model_name="saleitem",
            name="quantity",
            field=models.PositiveIntegerField(),
        ),
    ]