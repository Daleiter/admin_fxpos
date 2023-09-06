from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext


class ModelSharePointList:
    def __init__(self, list_name) -> None:
        self._user = 'b.burko@lvivkholod.com'
        self._paswd = 'Cthdbc@1'
        self._site = 'https://lvivkholod.sharepoint.com/sites/MS365'
        self._list_name = list_name
        self._list = None
        self._sp_item = None
        self._connect_to_sp()
    
    def __str__(self):
        res = ''
        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                res = res + f"type: {type(self.__getattribute__(k))}, name: {k}, value: {v}\n"
        return res

    def _connect_to_sp(self):
        user_credentials = UserCredential(self._user, self._paswd)
        self._ctx = ClientContext(self._site).with_credentials(user_credentials)
        self._list = self._ctx.web.lists.get_by_title(self._list_name)

    def _get_data_all(self):
        self._items = self._list.items.get_all(5000).execute_query()
        return self._items 

    def set_atributes(self):
        for k, v in self.__dict__.items():
            if k in self._one_item[0].properties:
                self.__setattr__(k, self._one_item[0].properties[k])
    
    def update(self):
        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                self._sp_item.set_property(k, v).update().execute_query()
        
    def _filter(self, email):
        tmp_l = self._get_data_all()
        for tmp_item in tmp_l:
            if tmp_item.properties['email'] == email:
                return tmp_item
                
    def save(self):
        d_to_save = {}
        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                d_to_save[k]= v
        self._sp_item = self._list.add_item(d_to_save).execute_query()


    def filter_one(self, condition):
        filtered_instances = []
        all_instances = self.all()
        for instance in all_instances:
            if condition(instance):
                filtered_instances.append(instance)
        if len(filtered_instances) == 0:
            return None
        return filtered_instances[0]
    

    def filter_all(self, condition):
        filtered_instances = []
        all_instances = self.all()
        for instance in all_instances:
            if condition(instance):
                filtered_instances.append(instance)
        return filtered_instances


    def all(self):
        res_all = []
        self._get_data_all()
        for item in self._items:
            tmp_item = self.__class__()  # Initialize a new instance of the same class
            tmp_item.__dict__.update(item.properties)  # Update attributes with properties
            tmp_item._sp_item = item
            res_all.append(tmp_item)
        return res_all