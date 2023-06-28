import unittest
from app import app, db
from models import Cupcake


class CupcakeViewsTestCase(unittest.TestCase):
    """Tests for views of API."""

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///cupcakes_test'
        app.config['SQLALCHEMY_ECHO'] = False
        return app

    def setUp(self):
        self.app = app  # Assign app instance to self.app
        with self.app.app_context():
            db.drop_all()
            db.create_all()

            self.cupcake_data = {
                "flavor": "TestFlavor",
                "size": "TestSize",
                "rating": 5,
                "image": "http://test.com/cupcake.jpg"
            }

            self.cupcake_data_2 = {
                "flavor": "TestFlavor2",
                "size": "TestSize2",
                "rating": 10,
                "image": "http://test.com/cupcake2.jpg"
            }

            cupcake = Cupcake(**self.cupcake_data)
            db.session.add(cupcake)
            db.session.commit()

            self.cupcake = cupcake

    def tearDown(self):
        with self.app.app_context():
            db.session.rollback()

    def test_get_cupcake(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                cupcake = Cupcake.query.filter_by(flavor='TestFlavor').first()
            url = f"/api/cupcakes/{cupcake.id}"
            resp = client.get(url)

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {
                "cupcake": {
                    "id": cupcake.id,
                    "flavor": "TestFlavor",
                    "size": "TestSize",
                    "rating": 5,
                    "image": "http://test.com/cupcake.jpg"
                }
            })

    def test_list_cupcakes(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                cupcake = Cupcake.query.filter_by(flavor='TestFlavor').first()
            resp = client.get("/api/cupcakes")

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {
                "cupcakes": [
                    {
                        "id": cupcake.id,
                        "flavor": "TestFlavor",
                        "size": "TestSize",
                        "rating": 5,
                        "image": "http://test.com/cupcake.jpg"
                    }
                ]
            })


    def test_create_cupcake(self):
        with self.app.test_client() as client:
            url = "/api/cupcakes"
            resp = client.post(url, json=self.cupcake_data_2)

            self.assertEqual(resp.status_code, 201)

            data = resp.json

            # Don't know what ID we'll get, make sure it's an int & normalize
            self.assertIsInstance(data['cupcake']['id'], int)
            del data['cupcake']['id']

            self.assertEqual(data, {
                "cupcake": {
                    "flavor": "TestFlavor2",
                    "size": "TestSize2",
                    "rating": 10,
                    "image": "http://test.com/cupcake2.jpg"
                }
            })

            self.assertEqual(Cupcake.query.count(), 2)


if __name__ == '__main__':
    unittest.main()
