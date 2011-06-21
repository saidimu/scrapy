from scrapy.item import Field, Item, ItemMeta


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
#                    import pdb; pdb.set_trace()
#                    cls._values[model_field.name] = model_field.value_from_object[cls]  ## copy Django model instance values into DjangoItem
#        import pdb; pdb.set_trace()
        return cls


class DjangoItem(Item):

    __metaclass__ = DjangoItemMeta

    django_model = None
    django_instance = None
    
#    def save(self, commit=True):
#        modelargs = dict((f, self.get(f, None)) for f in self._model_fields)
#        import pdb; pdb.set_trace()
#        model = self.django_model(**modelargs)
#        if commit:
#            model.save()
#        return model
    def populate_fields(self):
        if self.django_instance:
            return
        
#        modelargs = dict((f, self.get(f, None)) for f in self._model_fields)
        modelargs = {}
        for f in self._model_fields:
            if self.get(f, None):
                modelargs[f] = self.get(f, None)
                              
#        self.django_instance = self.django_model(**modelargs)
#        self.django_instance = self.django_model.objects.get(**modelargs)   ## assuming only 1 result
        self._values['django_instance'] = self.django_model.objects.get(**modelargs)   ## assuming only 1 result
        
        ## now populate empty fields in this Item with values from the just-retrieved django instance
        for f in self._model_fields:
            if not self.get(f, None):
                self[f] = getattr(self['django_instance'], f)
        import pdb; pdb.set_trace()
        
        
    def save_to_db(self):
        if not self.django_instance:
            self.populate_item()

        self.django_instance = self.django_instance.save()
        return self.django_instance
