from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import pandas as pd
import numpy as np


class StoreMeger(BaseEstimator, TransformerMixin):
    
    def fit(self, X, y= None):
        return self
    
    def transform(self, X):
        stores_df = pd.read_csv('data/stores.csv')

        stores_df_transformed = stores_df.drop(['city', 'state', 'type'], axis=1)
        merged_store_df = pd.merge(X, stores_df_transformed, on=['store_nbr','store_nbr'])
        return merged_store_df.drop(['store_nbr'], axis=1)
    

class HolidayMerger(BaseEstimator, TransformerMixin):
    
    def fit(self, X, y= None):
        return self
    
    def transform(self, X):
        holidays_df = pd.read_csv('data/holidays_events.csv')

        mask = holidays_df['transferred'].apply(lambda x: x is False)
        holidays_filtered = holidays_df[mask].copy()
        holidays_filtered['is_holiday'] = True
        holidays_filtered = holidays_filtered.drop(['type', 'locale', 'locale_name', 'description', 'transferred'], axis=1)
        holidays_filtered = holidays_filtered.drop_duplicates()
        merged_holiday_df = pd.merge(X, holidays_filtered, on=['date', 'date'], how='left')
        merged_holiday_df.is_holiday = merged_holiday_df.is_holiday.fillna(False)
        return merged_holiday_df


class OilMerger(BaseEstimator, TransformerMixin):
    
    def fit(self, X, y= None):
        return self
    
    def transform(self, X):
        oil_df = pd.read_csv('data/oil.csv')
        filled_oil_df = oil_df.copy()
        filled_oil_df['oil_price'] = oil_df.dcoilwtico.ffill().bfill()
        filled_oil_df = filled_oil_df.drop(['dcoilwtico'], axis=1)
        merged_oil_df = pd.merge(X, filled_oil_df, on=['date', 'date'], how='left')

        return merged_oil_df.bfill()
    

class DateTransformer(BaseEstimator, TransformerMixin):

    def fit(self, X, y= None):
        return self
    
    def transform(self, X):
        X['date'] = pd.to_datetime(X['date'])
        X['month'] = X['date'].dt.month
        # X['day'] = X['date'].dt.day
        X['year'] = X['date'].dt.year
        X['day_of_week'] = X['date'].dt.dayofweek
        return X.drop(['date'], axis=1)
    

class IdDropper(BaseEstimator, TransformerMixin):
        
        def fit(self, X, y= None):
            return self
        
        def transform(self, X):
            return X.drop(['id'], axis=1)


class OneHotEncoder(BaseEstimator, TransformerMixin):
    
    def fit(self, X, y= None):
        return self
    
    def transform(self, X):
        return pd.get_dummies(X, columns=['family'])
    

def cap_sales(s, cap = 20000):
    return s.map(lambda x: x if x < cap else cap)


data_transform_pipeline = Pipeline([
     ('merge_stores', StoreMeger()),
     ('merge_holidays', HolidayMerger()),
    ('merge_oil_prices', OilMerger()),
    ('transform_dates', DateTransformer()),
    ('drop_id', IdDropper()),
    ('one_hot_encoding', OneHotEncoder()),
    ('min_max_scale', MinMaxScaler())
])
