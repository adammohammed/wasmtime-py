import unittest

from wasmtime import *


class TestStore(unittest.TestCase):
    def test_smoke(self):
        Store()
        Store(Engine())

    def test_errors(self):
        with self.assertRaises(TypeError):
            Store(3)  # type: ignore

    def test_interrupt_handle(self):
        config = Config()
        config.epoch_interruption = True
        engine = Engine(config)
        engine.increment_epoch()
        store = Store(engine)
        store.set_epoch_deadline(1)

    def test_interrupt_wasm(self):
        config = Config()
        config.epoch_interruption = True
        engine = Engine(config)
        store = Store(engine)

        module = Module(store.engine, """
            (import "" "" (func))
            (func
                call 0
                (loop br 0))
            (start 1)
        """)
        interrupt = Func(store, FuncType([], []), lambda: engine.increment_epoch())
        with self.assertRaises(Trap):
            Instance(store, module, [interrupt])

    def test_fuel(self):
        store = Store()

        with self.assertRaises(WasmtimeError):
            store.add_fuel(1)
        with self.assertRaises(WasmtimeError):
            store.fuel_consumed()

        config = Config()
        config.consume_fuel = True
        store = Store(Engine(config))
        store.add_fuel(1)
        assert(store.fuel_consumed() == 0)
        assert(store.consume_fuel(0) == 1)
        store.add_fuel(1)
        assert(store.consume_fuel(1) == 1)
        with self.assertRaises(WasmtimeError):
            store.consume_fuel(2)
