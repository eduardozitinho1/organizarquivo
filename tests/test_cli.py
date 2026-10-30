from organizarquivo.cli import main


def test_main_without_args_returns_1(capsys):
    assert main([]) == 1
    captured = capsys.readouterr()
    assert "uso:" in captured.err


def test_main_with_two_args_returns_1():
    assert main(["a", "b"]) == 1


def test_main_on_nonexistent_returns_1(capsys):
    assert main(["/caminho/que/nao/existe"]) == 1
    captured = capsys.readouterr()
    assert "Erro" in captured.err


def test_main_on_empty_folder_returns_0(tmp_path, capsys):
    assert main([str(tmp_path)]) == 0
    captured = capsys.readouterr()
    assert "Nada para organizar" in captured.out
