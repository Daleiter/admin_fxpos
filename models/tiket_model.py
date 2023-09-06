#from admin_fxpos.utils.sharepoint_olm import ModelSharePointList
import json
from datetime import date
from models.db_model import Incedent, Incedent_schema, Problem, Problem_schema, Phones, Shops, Shops_schema
from office365.sharepoint.fields.user_value import FieldUserValue
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext


class ModelSharePointList:
    def __init__(self, list_name) -> None:
        self._user = 'poweruser.ux@lvivkholod.com'
        self._paswd = 'xs8.Y6RRZ8eB'
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
    
    def get_users(self):
        users = self._ctx.web.site_users.select(["LoginName"]).get().execute_query()
        return users.to_json()


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

    def system_update(self):
        d_to_save = {}
        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                d_to_save[k]= v
        self._sp_item.validate_update_list_item(d_to_save, dates_in_utc=True).execute_query()
        
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


class Tiket(ModelSharePointList):
    def __init__(self) -> None:
        """ Title : Ід магазину + проблематика
            Stan: треба ставити закрито (можна поставити: нова, в роботі, відхилено)
            Department2Id:  має бути цифра 26 це код нашого департаменту в хелпдеск 
            Type2Id: заначення=149 це код типу проблеми 
            WhoId: 3085, id хто виконує 
            WhoStringId: 3085, як строка  id хто виконує
            ControlId" 3085, id Марічки 
            ControlStringId: 3085, id Марічки 
            AuthorId: 3116, id постановника 
            EditorId: 3116,  id постановника
            item_text  коментар до задачі"""
        self.Title = str()
        self.Stan = str()
        self.Department2Id = str()
        self.Type2Id = str()
        self.Item2Id = str()
        self.Who = str()
        self.Control = str()
        self.Editor = str()
        self.comm = str()
        self.DataFinisch = date.today().isoformat()
        self.DatePlan = date.today().isoformat()
        self.DataAp = date.today().isoformat()
        self.PlanDay = str()
        self.Author = str()
        super().__init__('HDesk')

    def to_dict(self):
        obj_dict = {}
        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                obj_dict[k]= v
        return obj_dict

def create_help_desk_tiket(incedent):
    tiket = Tiket()
    shop = Shops.query.filter(Shops.id==incedent.id_shop).one()
    Author = FieldUserValue.from_user(tiket._ctx.web.site_users.get_by_email(shop.email))
    performer = FieldUserValue.from_user(tiket._ctx.web.site_users.get_by_email(incedent.user))
    problem = Problem.query.filter(Problem.id==incedent.id_problem).one()
    tiket.Title = f"РК {shop.shop_number}, {shop.name}, проблематика - {incedent.add_info['type_incedent_from_line']}"
    tiket.Author = Author
    tiket.Stan = "виконано"
    tiket.Department2Id = "26"
    tiket.Type2Id = "149"
    tiket.Who = performer
    tiket.Item2Id = "534"
    tiket.Control = FieldUserValue.from_user(tiket._ctx.web.site_users.get_by_email("m.kukiz@lvivkholod.com"))
    tiket.Editor = Author
    tiket.DataFinisch = incedent.time_finish.isoformat()
    tiket.DatePlan = incedent.time_finish.isoformat()
    tiket.DataAp = date.today().isoformat()
    tiket.PlanDay = 1
    tiket.comm = f"Заявка прийнята з номеру: {incedent.add_info['callerid']} \nПроблематика - {problem.name}\nРезультат:\n{incedent.result}"
    tiket.save()
    tiket._sp_item.validate_update_list_item({"Author": Author}).execute_query()
    
