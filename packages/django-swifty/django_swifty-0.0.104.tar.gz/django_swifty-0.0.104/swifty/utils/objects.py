# -*- coding: utf-8 -*-
from collections.abc import Mapping


class AbstractDictObject(Mapping):
    """
    _summary_

    Args:
        object (_type_): _description_
    """


class DotList(list):
    """
    _summary_

    Args:
        list (_type_): _description_
    """

    def __getattr__(self, name):
        """
        _summary_

        Args:
            name (_type_): _description_

        Raises:
            AttributeError: _description_

        Returns:
            _type_: _description_
        """
        try:
            return DotList(
                [
                    item
                    for sublist in self
                    for item in (
                        getattr(sublist, name)
                        if sublist and isinstance(getattr(sublist, name, None), DotList)
                        else (
                            [
                                (
                                    getattr(sublist, name)
                                    if hasattr(sublist, name)
                                    else sublist.get(name)
                                )
                            ]
                            if sublist
                            else [sublist]
                        )
                    )
                ]
            )
        except (ValueError, IndexError) as exc:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            ) from exc

    def __call__(self):
        pass


class DictObject(AbstractDictObject):
    """Convert dictionary to object with accessed attributes

    Args:
        object (_type_): _description_
    """

    def __init__(self, dict_data, depth=2):
        """_summary_

        Args:
            dict_data (_type_): _description_
            depth (int, optional): _description_. Defaults to 2.
        """
        depth -= 1
        self._dict_data = dict_data
        for key, value in (dict_data or {}).items():
            if depth <= 0:
                setattr(self, key, value)
            elif isinstance(value, (list, tuple)):
                setattr(
                    self,
                    key,
                    DotList(
                        [
                            (
                                DictObject(
                                    item,
                                    depth=depth,
                                )
                                if isinstance(item, dict)
                                else item
                            )
                            for item in value
                        ]
                    ),
                )
            else:
                setattr(
                    self,
                    key,
                    (
                        DictObject(value, depth=depth)
                        if isinstance(value, dict)
                        else value
                    ),
                )

    def __getitem__(self, key):
        return getattr(self, key, None)

    def __iter__(self):
        return iter(self._dict_data)

    def __len__(self):
        return self._dict_data and len(self._dict_data) or 0
