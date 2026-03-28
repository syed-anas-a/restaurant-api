from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0005_orderitem_price_alter_order_order_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='category',
            field=models.CharField(
                choices=[
                    ('appetizer', 'Appetizer'),
                    ('main_course', 'Main Course'),
                    ('dessert', 'Dessert'),
                    ('beverage', 'Beverage'),
                ],
                default='main_course',
                max_length=25,
            ),
        ),
    ]
