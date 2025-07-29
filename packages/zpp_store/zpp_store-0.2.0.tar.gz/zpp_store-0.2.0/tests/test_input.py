# test_secure_input.py

import zpp_store.input as secure

def test_secure_input(monkeypatch, capsys):
    keys = [ord('a'), ord('b'), ord('c'), 13]
    keys_iter = iter(keys)

    def fake_getch():
        return chr(next(keys_iter))

    # Patch le bon module : secure, pas zpp_store !
    monkeypatch.setattr(secure, 'getch', fake_getch)

    result = secure.secure_input(prompt="Enter: ", mask='*')
    captured = capsys.readouterr()

    assert result == 'abc'
    assert "Enter: " in captured.out
    assert captured.out.count('*') == 3
