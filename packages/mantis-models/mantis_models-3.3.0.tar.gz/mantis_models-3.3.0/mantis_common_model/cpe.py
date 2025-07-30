# -*- coding: utf-8 -*-
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Tuple

import packaging.version
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator
from pydantic import model_serializer
from pydantic import model_validator


class CpeModel(BaseModel):

    cpe_version: str
    part: str
    vendor: str
    product: str
    version: str
    update: str
    edition: str
    language: str
    sw_edition: str
    target_sw: str
    target_hw: str
    other: str

    model_config = ConfigDict(from_attributes=True)  # mandatory to use "model_validate" class method

    @model_serializer()
    def serialize_model(self):
        return f"cpe:{self.cpe_version}:{self.part}:{self.vendor}:{self.product}:{self.version}:{self.update}:{self.edition}:{self.language}:{self.sw_edition}:{self.target_sw}:{self.target_hw}:{self.other}"

    @model_validator(mode="before")
    @classmethod
    def from_any(cls, v: Any) -> Dict:
        if isinstance(v, str):
            elements = v.split(":")
            if len(elements) != 13:
                raise Exception(
                    f"This cpe {v} does not contain the number of fields required ({len(elements)} instead of 13) for the CPE 2.3 specifications: {elements[1]}"
                )

            return dict(
                cpe_version=elements[1],
                part=elements[2],
                vendor=elements[3],
                product=elements[4],
                version=elements[5],
                update=elements[6],
                edition=elements[7],
                language=elements[8],
                sw_edition=elements[9],
                target_sw=elements[10],
                target_hw=elements[11],
                other=elements[12],
            )
        else:
            return v

    @field_validator("cpe_version")
    def check_version(cls, v):
        if v != "2.3":
            raise ValueError(f"This CPE version is not supported: {v[1]}")
        return v

    def __str__(self):
        return f"cpe:{self.cpe_version}:{self.part}:{self.vendor}:{self.product}:{self.version}:{self.update}:{self.edition}:{self.language}:{self.sw_edition}:{self.target_sw}:{self.target_hw}:{self.other}"

    # Checks that two CPEs are matching
    def compare(self, other: "CpeModel") -> bool:
        fields_to_compare = [
            "cpe_version",
            "part",
            "vendor",
            "product",
            "version",
            "update",
            "edition",
            "language",
            "sw_edition",
            "target_sw",
            "target_hw",
            "other",
        ]

        # Comparer chaque champ en utilisant les méthodes appropriées
        for field in fields_to_compare:
            self_value = getattr(self, field)
            other_value = getattr(other, field)

            # Utiliser `check_if_versions_compatible` pour la version, sinon `check_if_values_compatible`
            if field == "version":
                if not self.check_if_versions_compatible(self_value, other_value):
                    return False
            else:
                if not self.check_if_values_compatible(self_value, other_value):
                    return False
        return True

    def check_if_versions_compatible(self, a: str, b: str) -> bool:
        is_compatible = False
        if a == b:
            is_compatible = True
        else:
            try:
                version_a = packaging.version.parse(a)
                version_b = packaging.version.parse(b)

                if version_a == version_b:
                    is_compatible = True

            except Exception:
                is_compatible = False

            if is_compatible is False:
                if self.__in_range(a, b):
                    is_compatible = True

        return is_compatible

    def check_if_values_compatible(self, a: str, b: str) -> bool:
        is_compatible = False
        if a == "*" or b == "*":
            is_compatible = True
        elif a == "-" or b == "-":
            is_compatible = True
        elif a != b:
            is_compatible = False
        elif a == b:
            is_compatible = True
        return is_compatible

    # If x or y is a range, verifies that the other one is in this range
    def __in_range(self, x: str, y: str) -> bool:
        xsplit = x.split("-")
        ysplit = y.split("-")
        rnge = None  # "range" is a keyword
        v = None
        if len(xsplit) == 2 and len(ysplit) == 1:
            rnge = xsplit
            v = y
        elif len(xsplit) == 1 and len(ysplit) == 2:
            rnge = ysplit
            v = x
        else:
            return False

        try:
            version_rnge0 = packaging.version.parse(rnge[0])
            version_v = packaging.version.parse(v)
            version_rnge1 = packaging.version.parse(rnge[1])
        except Exception:
            return False

        return version_rnge0 <= version_v and version_v <= version_rnge1

    def contains_product(self, product_name: str) -> bool:
        contains: bool = False
        if product_name.lower() in self.product.lower():
            contains = True
        return contains


class CpeListModel(BaseModel):

    cpeItems: List[CpeModel]

    model_config = ConfigDict(from_attributes=True)  # mandatory to use "model_validate" class method

    @model_serializer()
    def serialize_model(self):
        return self.cpeItems

    @model_validator(mode="before")
    @classmethod
    def from_any(cls, v: Any) -> Dict:
        if isinstance(v, list):
            cpeItems = list()
            for cpe in v:
                cpeItems.append(cpe)
            return dict(cpeItems=cpeItems)
        else:
            return v

    def contains(
        self, other: "CpeListModel"
    ) -> bool:  # Uses the quotes to use a class within the same class
        """
        Checks that the current (self) CPE List model includes the second cpes (all of them are known)
        """
        contains: bool = False
        for a_cpe in self.cpeItems:
            for b_cpe in other:
                if a_cpe.compare(b_cpe) is True:
                    contains = True
                    break
        return contains

    def get_o_parts(self) -> "CpeListModel":
        """
        Builds a new CpeListModel with operating system ('o') parts only
        """
        return self.__get_parts("o")

    def get_a_parts(self) -> "CpeListModel":
        """
        Builds a new CpeListModel with application ('a') parts only
        """
        return self.__get_parts("a")

    def __get_parts(self, part: str) -> "CpeListModel":

        cpeItems = list()

        for item in self.cpeItems:
            if item.part == part:
                cpeItems.append(item)

        extracted = CpeListModel(cpeItems=cpeItems)

        return extracted

    def __iter__(self) -> Iterator[CpeModel]:  # type: ignore
        return iter(self.cpeItems)

    def __getitem__(self, index: int) -> CpeModel:
        return self.cpeItems[index]

    def __len__(self) -> int:
        return len(self.cpeItems)

    def _get_part(self, cpe: str) -> Tuple[bool, str]:  # -> (error, result)
        cpe_part = cpe.split(":")
        if len(cpe_part) >= 2:
            part = cpe_part[2]
            if not (part == "o" or part == "a"):
                return (False, part)
            return (True, part)
        else:
            return (False, "")

    def contains_product(self, product_name: str) -> bool:
        contains: bool = False
        for x in self.cpeItems:
            if x.contains_product(product_name):
                contains = True
                break
        return contains
