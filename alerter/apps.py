from django.apps import AppConfig

class config(AppConfig):
    name = 'alerter'
    verbose_name = "It rocks"
    
    def ready(self):
        import alerter.signals
        
