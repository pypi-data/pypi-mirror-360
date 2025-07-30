# -*- coding: utf-8 -*-
# Copyright © kakkarja (K A K)

from enum import StrEnum


class Choices(StrEnum):
    A = "A"
    B = "B"
    C = "C"

if __name__ == "__main__":
    c = Choices("A")
    print(f"{c}")