from django.apps import AppConfig


class PersonnelConfig(AppConfig):
    name = 'personnel'

    def ready(self):
        import personnel.signals # noqa
