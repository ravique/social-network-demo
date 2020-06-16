from django.utils.timezone import now

from sn_test_task.redis import redis_instance


def request_middleware(get_response):
    def last_user_request(request):
        response = get_response(request)
        if request.user.is_anonymous:
            return response

        request_moment = now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        redis_instance.set('_'.join(('user', str(request.user.id))), request_moment)
        return response

    return last_user_request
