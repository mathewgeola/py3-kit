import py3_kit


def test_types():
    class Base(
        metaclass=py3_kit.types.create_subclasscheck_meta_class(
            required_all_methods=("open", "close"),
            required_any_methods=("run",)
        )
    ):
        pass

    class A:
        def open(self):
            pass

        def close(self):
            pass

        def run(self):
            pass

    class B:
        def open(self):
            pass

        def run(self):
            pass

    print(issubclass(A, Base))
    print(issubclass(B, Base))


if __name__ == '__main__':
    test_types()
