from flask.helpers import url_for

from tests.abstract_tests import AFlaskTest
from bexi import Config
from bexi.addresses import create_unique_address


class TestIntegration(AFlaskTest):

    def setUp(self):
        super(TestIntegration, self).setUp()

        # allow broadcasting in this test!
        Config.data["bitshares"]["connection"]["Test"]["nobroadcast"] = False

    def invalidate(self, url, code, response_json=None, response_json_contains=None, method=None, body=None):
        if method is None:
            method = self.client.get
        if body:
            response = method(url, data=body)
        else:
            response = method(url)
        self.assertEqual(response.status_code, code)
        if response_json is not None:
            assert response.json == response_json
        if response_json_contains is not None:
            for key, value in response_json_contains.items():
                assert response.json[key] == value

    def test_address_validity(self):
        self.invalidate(url_for('Blockchain.Api.address_validity', address="!@$%^&*("),
                        200,
                        response_json={'isValid': False})
        self.invalidate(url_for('Blockchain.Api.address_validity', address="1234"),
                        200,
                        response_json={'isValid': False})

    def test_get_asset(self):
        response = self.client.get(url_for('Blockchain.Api.get_asset', assetId="1.3.0"))
        assert response.json == {'accuracy': 5, 'address': 'None', 'assetId': '1.3.0', 'name': 'BTS'}

        self.invalidate(url_for('Blockchain.Api.get_asset', assetId="!@&*("),
                        204)

        self.invalidate(url_for('Blockchain.Api.get_asset', assetId="1234"),
                        204)

    def test_get_assets(self):
        response = self.client.get(url_for('Blockchain.Api.get_all_assets', take="2"))
        assert response.json == {'continuation': 2, 'items': [{'accuracy': 5, 'address': 'None', 'assetId': '1.3.0', 'name': 'BTS'}, {'accuracy': 4, 'address': 'None', 'assetId': '1.3.121', 'name': 'USD'}]}

        response = self.client.get(url_for('Blockchain.Api.get_all_assets', take="2", continuation="2"))
        assert response.json == {'continuation': None, 'items': [{'accuracy': 4, 'address': 'None', 'assetId': '1.3.120', 'name': 'EUR'}]}

        self.invalidate(url_for('Blockchain.Api.get_all_assets', take="!@*()"),
                        400)

        self.invalidate(url_for('Blockchain.Api.get_all_assets', take="35.23"),
                        400)

        self.invalidate(url_for('Blockchain.Api.get_all_assets', take="35,23"),
                        400)

        self.invalidate(url_for('Blockchain.Api.get_all_assets', take=""),
                        400)

        self.invalidate(url_for('Blockchain.Api.get_all_assets', take=None),
                        400)

    def test_observe_address(self):
        self.invalidate(url_for('Blockchain.Api.observe_address', address="35.23"),
                        400,
                        method=self.client.post)

    def test_unobserve_address(self):
        self.invalidate(url_for('Blockchain.Api.unobserve_address', address="35.23"),
                        400,
                        method=self.client.delete)

    def test_get_balances(self):
        self.invalidate(url_for('Blockchain.Api.get_balances', take="!@*()"),
                        400)

        self.invalidate(url_for('Blockchain.Api.get_balances', take="35.23"),
                        400)

    def test_build_transaction(self):
        self.invalidate(url_for('Blockchain.Api.build_transaction'),
                        400,
                        method=self.client.post)

    def test_history(self):
        address = create_unique_address(self.get_customer_id())
        self.client.post(url_for('Blockchain.Api.observe_address_history_from', address=address))
        self.invalidate(url_for('Blockchain.Api.observe_address_history_from', address=address),
                        409,
                        method=self.client.post,
                        response_json_contains={"errorCode": "unknown"})

        self.client.delete(url_for('Blockchain.Api.unobserve_address_history_from', address=address))
        self.invalidate(url_for('Blockchain.Api.unobserve_address_history_from', address=address),
                        204,
                        method=self.client.delete)

        self.client.post(url_for('Blockchain.Api.observe_address_history_to', address=address))
        self.invalidate(url_for('Blockchain.Api.observe_address_history_to', address=address),
                        409,
                        method=self.client.post,
                        response_json_contains={"errorCode": "unknown"})

        self.client.delete(url_for('Blockchain.Api.unobserve_address_history_to', address=address))
        self.invalidate(url_for('Blockchain.Api.unobserve_address_history_to', address=address),
                        204,
                        method=self.client.delete)

    def test_broadcast_transaction(self):
        self.invalidate(url_for('Blockchain.Api.broadcast_transaction'),
                        400,
                        method=self.client.post,
                        body={"operationId": "adfd63e4-c362-4d38-b90e-cd0e0aec3762", "signedTransaction": "9bd781d436694c57b77e31274f764d60"})

