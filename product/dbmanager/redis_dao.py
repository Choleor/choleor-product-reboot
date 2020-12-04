from django_redis import get_redis_connection


class SelectionRedisHandler:
    dao = get_redis_connection("selection")

    @staticmethod
    def get_selection_info(user_id):  # for test
        return SelectionRedisHandler.dao.lrange(user_id, 0, -1).decode('UTF-8')

