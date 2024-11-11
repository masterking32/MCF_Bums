from datetime import datetime
import json

class StoreModel:
    def __init__(self):
        pass

    class StoreProp:
        def __init__(self, data: dict):
            self._data = data
            self._id = str(self._data.get("id", ""))
            self._title = str(self._data.get("title", ""))
            self._desc = str(self._data.get("desc", ""))
            self._url = str(self._data.get("url", ""))
            self._prop_id = int(self._data.get("propId", -999))
            self._prop_type_id = int(self._data.get("propTypeId", -999))
            self._prop_data = StoreModel.StorePropData(json.loads(self._data.get("propData", "{}")))
            self._basic_num = int(self._data.get("basicNum", -999))
            self._basic_addition_num = int(self._data.get("basicAdditionNum", -999))
            self._basic_addition_ratio = int(self._data.get("basicAdditionRatio", -999))
            self._first_addition_num = int(self._data.get("firstAdditionNum", -999))
            self._first_state = int(self._data.get("firstState", -999))
            self._is_recommend = int(self._data.get("isRecommend", -999))
            self._is_hot = int(self._data.get("isHot", -999))
            self._is_good_value = int(self._data.get("isGoodValue", -999))
            self._sell_lists = [StoreModel.StorePropSellList(sell) for sell in self._data.get("sellLists", [])]
            self._stock = int(self._data.get("stock", -999))
            self._is_buyed = bool(self._data.get("isBuy", False))
            self._today_used = int(self._data.get("toDayNowUseNum", -999))
            self._today_max_use = int(self._data.get("toDayMaxUseNum", -999))
            self._acquisition_method = self._data.get("acquisitionMethod", "")
            self._is_buy_allowed = bool(self._data.get("isAllowBuy", False))

        @property
        def id(self):
            return self._id
        
        @property
        def title(self):
            return self._title

        @property
        def desc(self):
            return self._desc
        
        @property
        def url(self):
            return self._url
        @property
        def prop_id(self):
            return self._prop_id
        @property
        def prop_type_id(self):
            return self._prop_type_id
        @property
        def prop_data(self):
            return self._prop_data
        @property
        def basic_num(self):
            return self._basic_num
        @property
        def basic_addition_num(self):
            return self._basic_addition_num
        @property
        def basic_addition_ratio(self):
            return self._basic_addition_ratio
        @property
        def first_addition_num(self):
            return self._first_addition_num
        @property
        def first_state(self):
            return self._first_state
        @property
        def is_recommend(self):
            return self._is_recommend
        @property
        def is_hot(self):
            return self._is_hot
        @property
        def is_good_value(self):
            return self._is_good_value
        @property
        def sell_lists(self):
            return self._sell_lists
        @property
        def stock(self):
            return self._stock
        @property
        def is_buyed(self):
            return self._is_buyed
        @property
        def today_used(self):
            return self._today_used
        @property
        def today_max_use(self):
            return self._today_max_use
        @property
        def acquisition_method(self):
            return self._acquisition_method
        @property
        def is_buy_allowed(self):
            return self._is_buy_allowed

    class StorePropSellList:
        def __init__(self, data: dict):
            self._data = data
            self._id = int(self._data.get("id", -999))
            self._pay_method = int(self._data.get("payMethod", -999))
            self._old_amount = float(self._data.get("oldAmount", -999))
            self._new_amount = float(self._data.get("newAmount", -999))
            self._buy_limit = int(self._data.get("limitBuyNum", -999))
            self._limit_single_buy_num_min = int(self._data.get("limitSingleBuyNumMin", -999))
            self._limit_single_buy_num_step = int(self._data.get("limitSingleBuyNumStep", -999))
            self._sale_start_time = self._data.get("saleStartTime")
            self._sale_end_time = self._data.get("saleEndTime")
            self._shelf_time = self._data.get("shelfTime")

        @property
        def id(self):
            return self._id
        
        @property
        def pay_method(self):
            return self._pay_method

        @property
        def old_amount(self):
            return self._old_amount
        @property
        def new_amount(self):
            return self._new_amount
        @property
        def buy_limit(self):
            return self._buy_limit
        @property
        def limit_single_buy_num_min(self):
            return self._limit_single_buy_num_min
        @property
        def limit_single_buy_num_step(self):
            return self._limit_single_buy_num_step
        @property
        def sale_start_time(self):
            return self._safe_parse_dt(self._sale_start_time)
        @property
        def sale_end_time(self):
            return self._safe_parse_dt(self._sale_end_time)
        @property
        def shelf_time(self):
            return self._safe_parse_dt(self._shelf_time)

        def _safe_parse_dt(self, date_str):
            if not date_str:
                return None
            try:
                return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                return None

    class StorePropData:
        def __init__(self, data: dict):
            self._data = data
            self._multiplier = self._data.get("Multiple", -999.0)
            self._duration = self._data.get("DurationSecond", -999)

        @property
        def multiplier(self):
            return self._multiplier

        @property
        def duration(self):
            return self._duration

    class LotteryData:
        def __init__(self, data: dict):
            self._data = data
            self._remaining_time = int(self._data.get("downTime", -999))
            self._pph = int(self._data.get("perHourPower", -999))
            self._total_earn = self._data.get("totalEarn", "")
            self._reward = int(self._data.get("rewardNum", -999))
            self._card_required = int(self._data.get("cardNumber", -999))
            self._card_remaining = int(self._data.get("resultNum", -999))

        @property
        def remaining_time(self):
            return self._remaining_time

        @property
        def pph(self):
            return self._pph
        
        @property
        def total_earn(self):
            return self._total_earn
        @property
        def reward(self):
            return self._reward
        @property
        def card_required(self):
            return self._card_required
        @property
        def card_remaning(self):
            return self._card_remaining
