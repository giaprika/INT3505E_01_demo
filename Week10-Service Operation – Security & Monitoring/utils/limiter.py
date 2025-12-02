from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,  # dùng IP của client
    default_limits=["100 per hour"],  # giới hạn mặc định
    storage_uri="memory://"  # lưu trạng thái rate limit trong bộ nhớ
)


limiter = Limiter(
    key_func=get_remote_address,  # dùng IP của client
    default_limits=["100 per hour"],  # giới hạn mặc định
    storage_uri="memory://"  # lưu trạng thái rate limit trong bộ nhớ
)