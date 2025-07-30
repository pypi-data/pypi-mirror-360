from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone

from pytest import fixture

from wafer.talks.models import Talk


User = get_user_model()


@fixture()
def disable_caching(settings):
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }


@fixture
def user(db):
    user = User.objects.create(
        username="theuser",
        first_name="Firstname",
        last_name="Lastname",
    )
    yield user
    user.delete()


@fixture
def create_talk(db):
    talks = []
    users = []
    def _create_talk(username="author", title="Hello World", status='S'):
        author, created = User.objects.get_or_create(username=username)
        if created:
            users.append(author)
        talk = Talk.objects.create(
            title=title,
            status=status,
            corresponding_author=author)
        talk.authors.set([author])
        talks.append(talk)
        return talk

    yield _create_talk

    for talk in talks:
        talk.delete()
    for user in users:
        user.delete()


@fixture
def talk(create_talk):
    return create_talk()


@fixture
def client(db, user):
    _client = Client()
    _client.force_login(user)
    return _client


@fixture()
def now(mocker):
    n = timezone.now()
    mocker.patch("django.utils.timezone.now", return_value=n)
    return n
