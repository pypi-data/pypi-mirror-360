#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import abc
import typing as t

from klovve.data.list import List as _List
import klovve.data.list
import klovve.debug


class ListTransformer[TInput, TOutput]:

    def __init__(self):
        klovve.debug.memory.new_object_created(ListTransformer, self)

    def is_item_accepted(self, item: TInput) -> bool:
        return True

    def output_item(self, item: TInput) -> TOutput:
        return item


class TransformingListObserver(_List.Observer):

    def __init__(self, destination_list: _List, transformer: "ListTransformer"):
        super().__init__()
        self.__destination_list = destination_list
        self.__transformer = transformer
        self.__destination_indexes = []

    def item_added(self, index, item):
        if self.__transformer.is_item_accepted(item):
            output_item = self.__transformer.output_item(item)
            destination_index = self.__to_destination_index(index, never_none=True)
            self.__destination_list.insert(destination_index, output_item)
        else:
            destination_index = None

        if destination_index is not None:
            for i in range(index, len(self.__destination_indexes)):
                if self.__destination_indexes[i] is not None:
                    self.__destination_indexes[i] += 1
        self.__destination_indexes.insert(index, destination_index)

    def item_moved(self, from_index, to_index, item):
        from_index_here = self.__to_destination_index(from_index)
        if from_index_here is not None:
            to_index_here = self.__to_destination_index(to_index, never_none=True)
            self.__destination_list.move(from_index_here, to_index_here)

        self.__destination_indexes.insert(to_index, self.__destination_indexes.pop(from_index))
        if from_index_here is not None:
            new_index = 0
            for i in range(len(self.__destination_indexes)):
                if self.__destination_indexes[i] is not None:
                    self.__destination_indexes[i] = new_index
                    new_index += 1

    def item_removed(self, index, item):
        index_here = self.__to_destination_index(index)
        if index_here is not None:
            self.__destination_list.pop(index_here)

        if index_here is not None:
            for i in range(index, len(self.__destination_indexes)):
                if self.__destination_indexes[i] is not None:
                    self.__destination_indexes[i] -= 1
        self.__destination_indexes.pop(index)

    def item_replaced(self, index, old_item, new_item):
        index_here = self.__to_destination_index(index)
        new_item_accepted = self.__transformer.is_item_accepted(new_item)
        if bool(new_item_accepted) == bool(index_here):
            if index_here is not None:
                self.__destination_list[index_here] = self.__transformer.output_item(new_item)
        else:
            if index_here is not None:
                self.__destination_list.pop(index_here)

                for i in range(index, len(self.__destination_indexes)):
                    if self.__destination_indexes[i] is not None:
                        self.__destination_indexes[i] -= 1
                self.__destination_indexes[index] = None

            else:
                index_here_2 = self.__to_destination_index(index, never_none=True)
                self.__destination_list.insert(index_here_2, self.__transformer.output_item(new_item))

                for i in range(index, len(self.__destination_indexes)):
                    if self.__destination_indexes[i] is not None:
                        self.__destination_indexes[i] += 1
                self.__destination_indexes[index] = index_here_2

    def __to_destination_index(self, input_index: int, *, never_none: bool = False) -> t.Optional[int]:
        result = self.__destination_indexes[input_index] if (input_index < len(self.__destination_indexes)) else None

        if (result is None) and never_none:
            input_index_ = input_index
            while result is None:
                input_index_ += 1
                if input_index_ >= len(self.__destination_indexes):
                    break
                result = self.__destination_indexes[input_index_]

            input_index_ = input_index
            while result is None:
                input_index_ -= 1
                if input_index_ < 0:
                    break
                result = self.__destination_indexes[input_index_]
                if result is not None:
                    result += 1

            result = result or 0

        return result


class ConcatenatingListObserver(_List.Observer):

    def __init__(self, destination_list: _List, after_lists: t.Iterable[list]):
        super().__init__()
        self.__destination_list = destination_list
        self.__after_lists = tuple(after_lists)

    def item_added(self, index, item):
        self.__destination_list.insert(self.__start_at_index() + index, item)

    def item_removed(self, index, item):
        self.__destination_list.pop(self.__start_at_index() + index)

    def item_moved(self, from_index, to_index, item):
        start_at_index = self.__start_at_index()
        self.__destination_list.insert(start_at_index + to_index,
                                       self.__destination_list.pop(start_at_index + from_index))

    def item_replaced(self, index, old_item, new_item):
        self.__destination_list[self.__start_at_index() + index] = new_item

    def __start_at_index(self):
        return sum(len(_) for _ in self.__after_lists)
