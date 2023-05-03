import unittest
from datetime import date
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactInput, PhoneOutput
from src.repository.contacts import (
    get_cnt_by_id,
    get_cnt,
    create_cnt,
    update_cnt,
    delete_cnt_by_id,
    get_birth_list
)


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):
    contact = None
    contacts = None
    body = None

    @classmethod
    def setUpClass(cls):
        cls.contact = Contact()
        cls.contacts = [Contact(), Contact(), Contact()]
        cls.body = ContactInput(
            first_name="Ben",
            last_name="Smith",
            email="test@example.com",
            birthday=date.today(),
            address=None,
            phones=[PhoneOutput(phone_num="380984561245"), PhoneOutput(phone_num="380991112233")]
        )

    @classmethod
    def tearDownClass(cls):
        cls.contact = None
        del cls.contacts
        cls.body = None

    def setUp(self):
        self.session = MagicMock(spec=Session)

    def tearDown(self):
        self.session = None

    async def test_get_birth_list_found(self):
        self.session.query().filter().order_by().all.return_value = self.contacts
        result = await get_birth_list(db=self.session)
        self.assertEqual(result, self.contacts)

    async def test_get_birth_list_not_found(self):
        self.session.query().filter().order_by().all.return_value = []
        result = await get_birth_list(db=self.session)
        self.assertEqual(result, [])

    async def test_get_cnt_by_id_found(self):
        self.session.query().get.return_value = self.contact
        result = await get_cnt_by_id(cnt_id=1, db=self.session)
        self.assertEqual(result, self.contact)

    async def test_get_cnt_by_id_not_found(self):
        self.session.query().get.return_value = None
        result = await get_cnt_by_id(cnt_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_get_cnt_found(self):
        self.session.query().filter().order_by().all.return_value = self.contacts
        self.session.query().order_by().all.return_value = self.contacts

        for f_type in range(0, 5):
            result = await get_cnt(db=self.session, filter_type=f_type, filter_str="test")
            self.assertEqual(result, self.contacts)

    async def test_get_cnt_not_found(self):
        self.session.query().filter().order_by().all.return_value = []
        self.session.query().order_by().all.return_value = []

        for f_type in range(0, 5):
            result = await get_cnt(db=self.session, filter_type=f_type, filter_str="test")
            self.assertEqual(result, [])

    async def test_create_cnt(self):
        result = await create_cnt(body=self.body, db=self.session)
        [self.assertEqual(result.__dict__[item],
                          self.body.__dict__[item]) for item in self.body.__dict__ if item != "phones"]
        self.assertEqual(result.phones[0].phone_num, "380984561245")
        self.assertTrue(hasattr(result, 'id'))

    async def test_update_cnt_found(self):
        self.session.query().get.return_value = self.contact
        result = await update_cnt(cnt_id=1, body=self.body, db=self.session)

        [self.assertEqual(result.__dict__[item],
                          self.body.__dict__[item]) for item in self.body.__dict__ if item != "phones"]
        self.assertEqual(result.phones[0].phone_num, "380984561245")

    async def test_update_cnt_not_found(self):
        self.session.query().get.return_value = None
        result = await update_cnt(cnt_id=1, body=self.body, db=self.session)
        self.assertIsNone(result)

    async def test_delete_cnt_by_id_found(self):
        self.session.query().get.return_value = self.contact
        result = await delete_cnt_by_id(cnt_id=1, db=self.session)
        self.assertEqual(result, self.contact)

    async def test_delete_cnt_by_id_not_found(self):
        self.session.query().get.return_value = None
        result = await delete_cnt_by_id(cnt_id=1, db=self.session)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
