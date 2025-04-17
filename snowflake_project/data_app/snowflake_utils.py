import os
import sys
import json
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from django.conf import settings

class SnowflakeConnector:
    def __init__(self):
        """初期化メソッド。Snowflake接続に必要な設定を取得します。"""
        config = settings.SNOWFLAKE_CONFIG
        self.user = config['user']
        self.account = config['account']
        self.role = config.get('role', '')
        self.warehouse = config['warehouse']
        self.database = config['database']
        self.schema = config['schema']
        self.private_key_path = config['private_key_path']
        # テーブル名をフルパスで定義
        self.pos_table = f"{self.database}.{self.schema}.POS_TEMP"
    
    # load_private_key メソッドと connect_to_snowflake メソッドは変更なし
    def load_private_key(self):
        try:
            # まず実行ファイルと同じディレクトリの秘密鍵を探す
            exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            external_key_path = os.path.join(exe_dir, 'rsa_key.p8')
            
            if os.path.exists(external_key_path):
                key_path = external_key_path
            else:
                # 見つからない場合はバンドルされた秘密鍵を使用
                key_path = self.get_resource_path('rsa_key.p8')
            
            with open(key_path, "rb") as key_file:
                private_key_data = key_file.read()
                
                private_key = serialization.load_der_private_key(
                    private_key_data,
                    password=None,  # 暗号化されていないことを前提
                    backend=default_backend()
                )
            
            return private_key

        except Exception as e:
            print(f"秘密鍵の読み込みに失敗しました: {e}")
            return None
        
    def connect_to_snowflake(self):
        """
        キーペア認証を使用してSnowflakeに接続します。
        
        :return: Snowflake接続オブジェクト
        """
        try:
            # 秘密鍵を読み込む
            private_key = self.load_private_key()
            if private_key is None:
                raise ValueError("秘密鍵のロードに失敗しました。")


            # Snowflake に接続（キーペア認証）
            conn = snowflake.connector.connect(
                user=self.user,
                account=self.account,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema,
                private_key=private_key  # パスワードの代わりに秘密鍵を使用
            )
            print("Snowflake にキーペア認証で接続しました。")
            return conn

        except Exception as e:
            print(f"Snowflake への接続に失敗しました: {e}")
            return None

    
    def get_pos_data(self, days=30, limit=100):
        """過去n日間のPOSデータを取得する"""
        conn = self.connect_to_snowflake()
        if conn:
            try:
                cursor = conn.cursor()
                # POS_TEMPテーブルから過去n日間のデータを取得（フルパスで指定）
                query = f"""
                SELECT 
                    SALES_DATE, PRODUCT_CODE, MAKER_CODE, MAKER_NAME, PRODUCT_NAME, 
                    STORE_CODE, STORE_NAME, SALES_NUMBER, SALES_AMOUNT, UNIT_PRICE,
                    CATEGORY1_NAME, CATEGORY2_NAME, CATEGORY3_NAME
                FROM {self.pos_table}
                WHERE SALES_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
                ORDER BY SALES_DATE DESC, SALES_AMOUNT DESC
                LIMIT {limit}
                """
                cursor.execute(query)
                # 結果を取得
                results = cursor.fetchall()
                # カラム名を取得
                columns = [col[0] for col in cursor.description]
                # 辞書のリストに変換
                data = []
                for row in results:
                    data.append(dict(zip(columns, row)))
                return data
            except Exception as e:
                print(f"POSデータの取得に失敗しました: {e}")
                return []
            finally:
                conn.close()
        return []
    
    def get_top_selling_products(self, days=30, limit=10):
        """過去n日間の売上上位商品を取得する"""
        conn = self.connect_to_snowflake()
        if conn:
            try:
                cursor = conn.cursor()
                query = f"""
                SELECT 
                    PRODUCT_CODE, PRODUCT_NAME, MAKER_NAME,
                    CATEGORY1_NAME, CATEGORY2_NAME, CATEGORY3_NAME,
                    SUM(SALES_NUMBER) as TOTAL_SALES_NUMBER,
                    SUM(SALES_AMOUNT) as TOTAL_SALES_AMOUNT,
                    AVG(UNIT_PRICE) as AVG_PRICE
                FROM {self.pos_table}
                WHERE SALES_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
                GROUP BY PRODUCT_CODE, PRODUCT_NAME, MAKER_NAME,
                    CATEGORY1_NAME, CATEGORY2_NAME, CATEGORY3_NAME
                ORDER BY TOTAL_SALES_AMOUNT DESC
                LIMIT {limit}
                """
                cursor.execute(query)
                results = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                data = []
                for row in results:
                    data.append(dict(zip(columns, row)))
                return data
            except Exception as e:
                print(f"売上上位商品の取得に失敗しました: {e}")
                return []
            finally:
                conn.close()
        return []
    
    def get_top_selling_categories(self, days=30, limit=5):
        """過去n日間の売上上位カテゴリを取得する"""
        conn = self.connect_to_snowflake()
        if conn:
            try:
                cursor = conn.cursor()
                query = f"""
                SELECT 
                    CATEGORY1_NAME, CATEGORY2_NAME,
                    SUM(SALES_AMOUNT) as TOTAL_SALES_AMOUNT,
                    COUNT(DISTINCT PRODUCT_CODE) as PRODUCT_COUNT
                FROM {self.pos_table}
                WHERE SALES_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
                GROUP BY CATEGORY1_NAME, CATEGORY2_NAME
                ORDER BY TOTAL_SALES_AMOUNT DESC
                LIMIT {limit}
                """
                cursor.execute(query)
                results = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                data = []
                for row in results:
                    data.append(dict(zip(columns, row)))
                return data
            except Exception as e:
                print(f"売上上位カテゴリの取得に失敗しました: {e}")
                return []
            finally:
                conn.close()
        return []
    
    def get_store_performance(self, days=1000, limit=10):
        """過去n日間の店舗別売上パフォーマンスを取得する"""
        conn = self.connect_to_snowflake()
        if conn:
            try:
                cursor = conn.cursor()
                query = f"""
                SELECT 
                    STORE_CODE, STORE_NAME,
                    SUM(SALES_AMOUNT) as TOTAL_SALES_AMOUNT,
                    COUNT(DISTINCT PRODUCT_CODE) as PRODUCT_COUNT,
                    COUNT(DISTINCT SALES_DATE) as SALES_DAYS
                FROM {self.pos_table}
                WHERE SALES_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
                GROUP BY STORE_CODE, STORE_NAME
                ORDER BY TOTAL_SALES_AMOUNT DESC
                LIMIT {limit}
                """
                cursor.execute(query)
                results = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                data = []
                for row in results:
                    data.append(dict(zip(columns, row)))
                return data
            except Exception as e:
                print(f"店舗別売上データの取得に失敗しました: {e}")
                return []
            finally:
                conn.close()
        return []
    
    def get_maker_performance(self, days=30, limit=10):
        """過去n日間のメーカー別売上パフォーマンスを取得する"""
        conn = self.connect_to_snowflake()
        if conn:
            try:
                cursor = conn.cursor()
                query = f"""
                SELECT 
                    MAKER_CODE, MAKER_NAME,
                    SUM(SALES_AMOUNT) as TOTAL_SALES_AMOUNT,
                    COUNT(DISTINCT PRODUCT_CODE) as PRODUCT_COUNT,
                    AVG(UNIT_PRICE) as AVG_PRICE
                FROM {self.pos_table}
                WHERE SALES_DATE >= DATEADD(day, -{days}, CURRENT_DATE())
                GROUP BY MAKER_CODE, MAKER_NAME
                ORDER BY TOTAL_SALES_AMOUNT DESC
                LIMIT {limit}
                """
                cursor.execute(query)
                results = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                data = []
                for row in results:
                    data.append(dict(zip(columns, row)))
                return data
            except Exception as e:
                print(f"メーカー別売上データの取得に失敗しました: {e}")
                return []
            finally:
                conn.close()
        return []