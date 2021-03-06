from scrapy.item import Field, Item, ItemMeta
from scrapy.http import Response

class DjangoItemMeta(ItemMeta):

    def  __new__(mcs, class_name, bases, attrs):
        cls = super(DjangoItemMeta, mcs).__new__(mcs, class_name, bases, attrs)
        cls.fields = cls.fields.copy()

        if cls.django_model:
            cls._model_fields = []
            cls._model_meta = cls.django_model._meta
            for model_field in cls._model_meta.fields:
                if model_field.auto_created == False:
                    if model_field.name not in cls.fields:
                        cls.fields[model_field.name] = Field()
                    cls._model_fields.append(model_field.name)
        return cls


class DjangoItem(Item):

    __metaclass__ = DjangoItemMeta

    django_model = None
    django_instance = None  ## FIXME: TODO: this doesn't seem to be needed any more. Remove?
    
    def populate_fields(self):
        if self.django_instance:
            return
        
        modelargs = {}
        for f in self._model_fields:
            if self.get(f, None):
                modelargs[f] = self.get(f, None)
                              
        self._values['django_instance'] = self.django_model.objects.get(**modelargs)   ## FIXME: assuming only 1 result
        
        ## now populate empty fields in this Item with values from the just-retrieved django instance
        for f in self._model_fields:
            if not self.get(f, None):
                self[f] = getattr(self['django_instance'], f)        
        
    def save_to_db(self):        
        if not self['django_instance']:    ## TODO: FIXME: will this overwrite field values in an Item instance with some fields already filled?
            self.populate_fields()

        ## copy values from this Item instance into the Django instance, then save the Django instance
        ## FIXME: TODO: I really shouldn't be setting the primary-key as well. Find a way to exclude it.
        for model_field in self._model_fields:
            setattr(self._values['django_instance'], model_field, self[model_field])
            
        self._values['django_instance'] = self._values['django_instance'].save()
        return self['django_instance']
