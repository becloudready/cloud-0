import snowflake.connector as sf
from config import SF_config as config

conn = sf.connect(user=config.username, password=config.password, account=config.account)