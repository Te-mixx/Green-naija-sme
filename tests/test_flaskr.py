def test_home(client):
    res = client.get("/")
    print(res)
    assert res.status_code == 200