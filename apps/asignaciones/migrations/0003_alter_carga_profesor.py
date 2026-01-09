# Generated manually for guardado parcial de cargas

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('academico', '0001_initial'),
        ('asignaciones', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carga',
            name='profesor',
            field=models.ForeignKey(
                blank=True,
                help_text='Opcional para permitir guardado parcial (borrador)',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='cargas',
                to='academico.profesor'
            ),
        ),
    ]
