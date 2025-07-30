import pytest
from flask import Flask, redirect, render_template_string
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# noinspection PyUnresolvedReferences
from flask_back import Back



@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "test"
    back = Back()
    back.init_app(app, excluded_endpoints={"excluded"}, default_url="/fallback", use_referrer=True)

    @app.route("/save")
    @back.save_url
    def save():
        return "saved"
    
    @app.route("/go-back")
    @back.exclude
    def go_back():
        return redirect(back.get_url())

    @app.route("/excluded")
    @back.exclude
    def excluded():
        return "excluded"

    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_save_url(client):
    res = client.get("/save")
    assert res.status_code == 200
    with client.session_transaction() as sess:
        assert sess["back_url"].endswith("/save")


def test_get_back_url(client):
    client.get("/save")
    res = client.get("/go-back", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["Location"].endswith("/save")



def test_excluded_endpoint(client):
    client.get("/excluded")
    with client.session_transaction() as sess:
        assert "back_url" not in sess


def test_get_url_with_referrer(client):
    res = client.get("/go-back", headers={"Referer": "/referrer"}, follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["Location"].endswith("/referrer")



def test_get_url_with_fallback(client):
    res = client.get("/go-back", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["Location"].endswith("/fallback")



def test_template_injection(client, app):
    back = app.extensions["back"]
    
    @app.route("/template-test")
    @back.exclude
    def template_test():
        return render_template_string("Back to: {{ back_url }}")


    with client:
        client.get("/save")  # sets session['back_url']
        res = client.get("/template-test")
        assert b"/save" in res.data
