import torch, torch.nn as nn, sys, pathlib

sys.path.append(pathlib.Path(__file__).parent.parent.as_posix())
from src.torchenhanced import Trainer, DevModule, ConfigModule
import os, shutil

curfold = pathlib.Path(__file__).parent


def test_kwargs():
    class LinSimple(ConfigModule):
        def __init__(self, hidden=28 * 28, out=10, device="cpu", **kwargs):
            super().__init__()

            self.layer = nn.Linear(hidden, out)

        def forward(self, x):
            return self.layer(x)

    model = LinSimple(hidden=28, out=5, device="cuda:0", extra="extra")
    testimony = torch.zeros((1, 1)).to("cuda:0")
    assert model.config == {
        "hidden": 28,
        "out": 5,
        "device": "cuda:0",
        "extra": "extra",
    }, f'found {model.config=} instead of {{"hidden": 28, "out": 5, "device": "cuda:0", "extra": "extra"}}'
    assert model.device == testimony.device, f"found {model.device=} instead of cuda:0"

    model = LinSimple()
    testimony = testimony.to("cpu")
    assert model.config == {
        "hidden": 28 * 28,
        "out": 10,
        "device": "cpu",
    }, f'found {model.config=} instead of {{"hidden": 28*28, "out": 10, "device": "cpu"}}'
    assert model.device == testimony.device, f"found {model.device=} instead of cpu"


def test_save_and_load():
    shutil.rmtree(os.path.join(curfold, "test_torchenhanced"), ignore_errors=True)
    os.makedirs(os.path.join(curfold, "test_torchenhanced"), exist_ok=True)

    class LinSimple(ConfigModule):
        def __init__(self, hidden=28 * 28, out=10, device="cpu", **kwargs):
            super().__init__()

            self.layer = nn.Linear(hidden, out)

        def forward(self, x):
            return self.layer(x)

    def check_same(model1, model2):
        for (name1, param1), (name2, param2) in zip(model1.state_dict().items(), model2.state_dict().items()):
            # Check parameter names match
            assert name1 == name2, f"Parameter names don't match: {name1} vs {name2}"
            # Check parameter values match using torch.allclose
            assert torch.allclose(param1, param2), f"Parameter values don't match for {name1}"

    model = LinSimple(hidden=28, out=5, device="cpu", extra="extra")

    model.save_config(os.path.join(curfold, "test_torchenhanced"), "test")

    model2 = LinSimple.from_config(os.path.join(curfold, "test_torchenhanced", "test.config"), device="cpu")

    assert model2.config == model.config, f"found {model2.config=} instead of {model.config}"

    check_same(model, model2)

    model3 = LinSimple(hidden=28, out=5, device="cpu", extra="extra")
    model3.load_config(os.path.join(curfold, "test_torchenhanced", "test.config"), device="cpu")

    assert model3.config == model.config, f"found {model3.config=} instead of {model.config}"
    check_same(model, model3)


def test_no_device():
    class LinSimple(ConfigModule):
        def __init__(self, hidden=28 * 28, out=10, **kwargs):
            super().__init__(device="cpu")

            self.layer = nn.Linear(hidden, out)

        def forward(self, x):
            return self.layer(x)

    model = LinSimple(hidden=28, out=5, extra="extra")
    testimony = torch.zeros((1, 1)).to("cpu")
    assert model.config == {
        "hidden": 28,
        "out": 5,
        "extra": "extra",
    }, f'found {model.config=} instead of {{"hidden": 28, "out": 5, "extra": "extra"}}'
    assert model.device == testimony.device, f"found {model.device=} instead of {testimony.device}"

    model = LinSimple(device="cuda:0")
    testimony = testimony.to("cuda:0")
    assert model.config == {
        "hidden": 28 * 28,
        "out": 10,
        "device": "cuda:0",
    }, f'found {model.config=} instead of {{"hidden": 784, "out": 10}}'
    assert model.device == testimony.device, f"found {model.device=} instead of cuda:0"


def test_no_kwargs():
    class LinSimple(ConfigModule):
        def __init__(self, hidden=28 * 28, out=10):
            super().__init__(device="cpu")

            self.layer = nn.Linear(hidden, out)

        def forward(self, x):
            return self.layer(x)

    model = LinSimple(hidden=22)
    testimony = torch.zeros((1, 1)).to("cpu")
    assert model.config == {"hidden": 22, "out": 10}, f'found {model.config=} instead of {{"hidden": 22, "out": 10}}'
    assert model.device == testimony.device, f"found {model.device=} instead of cpu"


if __name__ == "__main__":
    test_kwargs()
    test_no_device()
    print("All tests passed !")
