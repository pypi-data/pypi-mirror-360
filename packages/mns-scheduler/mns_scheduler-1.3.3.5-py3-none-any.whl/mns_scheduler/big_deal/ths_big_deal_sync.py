# import sys
# import os
#
# file_path = os.path.abspath(__file__)
# end = file_path.index('mns') + 17
# project_path = file_path[0:end]
# sys.path.append(project_path)
# import mns_common.utils.date_handle_util as date_handle_util
# from datetime import datetime, time, timedelta
# from loguru import logger
# import mns_common.utils.data_frame_util as data_frame_util
# from mns_common.db.MongodbUtil import MongodbUtil
# import mns_common.api.ths.big_deal.ths_big_deal_api as ths_big_deal_api
# import time as sleep_time
# import mns_common.constant.db_name_constant as db_name_constant
#
# mongodb_util = MongodbUtil('27017')
#
#
# #
# def get_last_number(str_day):
#     query = {'str_day': str_day}
#     big_deal_df = mongodb_util.descend_query(query, db_name_constant.BIG_DEAL_NAME, "number", 1)
#     if data_frame_util.is_empty(big_deal_df):
#         return 1
#     else:
#         return list(big_deal_df['number'])[0]
#
#
# def create_index():
#     mongodb_util.create_index(db_name_constant.BIG_DEAL_NAME, [("symbol", 1)])
#     mongodb_util.create_index(db_name_constant.BIG_DEAL_NAME, [("str_day", 1)])
#     mongodb_util.create_index(db_name_constant.BIG_DEAL_NAME, [("symbol", 1), ("str_day", 1)])
#     mongodb_util.create_index(db_name_constant.BIG_DEAL_NAME, [("number", 1), ("str_day", 1)])
#
#
# def sync_ths_big_deal(tag):
#     create_index()
#     now_date_begin = datetime.now()
#     str_day_begin = now_date_begin.strftime('%Y-%m-%d')
#     number = get_last_number(str_day_begin)
#     while True:
#         now_date = datetime.now()
#         begin_date = now_date + timedelta(minutes=-2)
#         if tag or date_handle_util.is_trade_time(now_date):
#             try:
#                 str_day = now_date.strftime('%Y-%m-%d')
#                 str_now_date = now_date.strftime('%Y-%m-%d %H:%M:%S')
#
#                 begin_str_date = begin_date.strftime('%Y-%m-%d %H:%M:%S')
#
#                 target_time_09_30 = time(9, 30)
#                 if now_date.time() < target_time_09_30:
#                     continue
#                 ths_big_deal_df = ths_big_deal_api.stock_fund_flow_big_deal(begin_str_date, str_now_date)
#                 if data_frame_util.is_empty(ths_big_deal_df):
#                     sleep_time.sleep(10)
#                     continue
#                 ths_big_deal_df['str_day'] = ths_big_deal_df['deal_time'].str.slice(0, 10)
#                 ths_big_deal_df = ths_big_deal_df.loc[ths_big_deal_df['str_day'] == str_day]
#                 ths_big_deal_df['number'] = number
#                 ths_big_deal_df['amount_str'] = ths_big_deal_df.amount.astype(str)
#                 ths_big_deal_df['type'] = ths_big_deal_df['type'].replace('买盘', 'buy')
#                 ths_big_deal_df['type'] = ths_big_deal_df['type'].replace("卖盘", "sell")
#
#                 ths_big_deal_df["_id"] = (ths_big_deal_df['deal_time'] + "-" + ths_big_deal_df['symbol'] + "-"
#                                           + ths_big_deal_df['amount_str'] + "-" + ths_big_deal_df['type'])
#                 ths_big_deal_df.drop_duplicates('_id', keep='last', inplace=True)
#                 ths_big_deal_df['sync_str_date'] = str_now_date
#                 # 设置卖盘为负数
#                 ths_big_deal_df.loc[ths_big_deal_df['type'] == 'sell', 'amount'] = -ths_big_deal_df.loc[
#                     ths_big_deal_df['type'] == 'sell', 'amount']
#
#                 ths_big_deal_df['chg'] = ths_big_deal_df['chg'].str.replace('%', '')
#                 ths_big_deal_df['chg'] = ths_big_deal_df['chg'].astype(float)
#
#                 del ths_big_deal_df['amount_str']
#                 exist_code_df = mongodb_util.find_query_data_choose_field(db_name_constant.BIG_DEAL_NAME,
#                                                                           {},
#                                                                           {"_id": 1})
#                 if data_frame_util.is_empty(exist_code_df):
#                     new_df = ths_big_deal_df
#                 else:
#                     exist_code_list = list(exist_code_df['_id'])
#                     new_df = ths_big_deal_df.loc[~(ths_big_deal_df['_id'].isin(exist_code_list))]
#
#                 if data_frame_util.is_empty(new_df):
#                     continue
#                 mongodb_util.insert_mongo(new_df, db_name_constant.BIG_DEAL_NAME)
#                 number = number + 1
#             except Exception as e:
#                 logger.error('策略执行异常:{}', e)
#         elif date_handle_util.is_close_time(now_date):
#             break
#
#
# if __name__ == '__main__':
#     sync_ths_big_deal(False)
