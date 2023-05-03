import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserInput
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    change_password,
    update_avatar
)


class TestUsersRepository(unittest.IsolatedAsyncioTestCase):
    user = None
    body = None
    email = None

    @classmethod
    def setUpClass(cls):
        cls.email = "test@example.com"
        cls.user = User()
        cls.body = UserInput(
            username="Ben",
            email="test@example.com",
            password="1234567"
        )

    @classmethod
    def tearDownClass(cls):
        cls.email = None
        cls.user = None
        cls.body = None

    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_user_by_email_found(self):
        self.session.query().filter_by().first.return_value = self.user
        result = await get_user_by_email(email=self.email, db=self.session)
        self.assertEqual(result, self.user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await get_user_by_email(email=self.email, db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        result = await create_user(body=self.body, db=self.session)
        [self.assertEqual(result.__dict__[item],
                          self.body.__dict__[item]) for item in self.body.__dict__]
        self.assertTrue(hasattr(result, 'id'))

    async def test_update_token(self):
        u_user = User(refresh_token="old_token")
        await update_token(user=u_user, refresh_token="new_token", db=self.session)
        self.assertEqual(u_user.refresh_token, "new_token")

    async def test_confirmed_email(self):
        u_user = User(confirmed=False)
        self.session.query().filter_by().first.return_value = u_user
        await confirmed_email(email=self.email, db=self.session)
        self.assertEqual(u_user.confirmed, True)

    async def test_change_password(self):
        u_user = User(password="old_password")
        new_password = "new_password"
        self.session.query().filter_by().first.return_value = u_user
        await change_password(user=u_user, password=new_password, db=self.session)
        self.assertEqual(u_user.password, new_password)

    async def test_update_avatar(self):
        u_user = User(avatar=None)
        image_url = "image_url"
        self.session.query().filter_by().first.return_value = u_user
        await update_avatar(email=self.email, url=image_url, db=self.session)
        self.assertEqual(u_user.avatar, image_url)


if __name__ == '__main__':
    unittest.main()
