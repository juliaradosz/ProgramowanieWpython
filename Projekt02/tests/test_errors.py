from unittest.mock import patch


class TestNotFound:
    def test_404_returns_404_status(self, client):
        response = client.get('/nie-ma-takiej-strony-xyz')
        assert response.status_code == 404

    def test_404_renders_custom_template(self, client):
        response = client.get('/nic-tu-nie-ma')
        assert b'404' in response.data


class TestInternalError:
    def test_500_handler_returns_500(self, app, client):
        @app.route('/__boom__')
        def boom():
            raise RuntimeError('something went wrong')

        response = client.get('/__boom__')
        assert response.status_code == 500

    def test_500_handler_renders_custom_template(self, app, client):
        @app.route('/__boom__')
        def boom():
            raise RuntimeError('boom')

        response = client.get('/__boom__')
        assert response.status_code == 500
        assert b'500' in response.data

    def test_500_handler_rolls_back_session(self, app, client):
        @app.route('/__boom__')
        def boom():
            raise RuntimeError('boom')

        with patch('app.errors.db.session.rollback') as mock_rollback:
            client.get('/__boom__')
            mock_rollback.assert_called_once()
