# -*- coding: utf-8 -*-
import json
import os
import sys
from typing import Any
from typing import Dict
from typing import List
from typing import Set

from pyattck import Attck  # type: ignore


# NOTE: the following imports are NOT dependencies of mantis_scenario_model
# If necessary, create a temporary venv to run this script:
# mkdir /tmp/myvenv
# python3 -m venv /tmp/myvenv
# source /tmp/myvenv/bin/activate
# pip3 install --upgrade pip
# pip install importlib_resources
# pip install pyattck


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MITRE_JSON_PATH = os.path.join(CURRENT_DIR, "mitre.json")


def list_difference(
    l1: List[Dict[str, Any]], l2: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    list_diff = []
    for e1 in l1:
        found = False
        for e2 in l2:
            if e1["id"] == e2["id"]:
                found = True
        if not found:
            list_diff.append(e1)

    return list_diff


def load_reference_mitre_data() -> Attck:
    print("Loading reference MITRE data")

    # attack object containing the reference information
    source_enterprise_attck_json = str(
        os.path.join(CURRENT_DIR, "merged_enterprise_attck_v2.json")
    )
    source_pre_attck_json = str(os.path.join(CURRENT_DIR, "merged_pre_attck_v1.json"))
    source_mobile_attck_json = str(
        os.path.join(CURRENT_DIR, "merged_mobile_attck_v2.json")
    )
    source_ics_attck_json = str(os.path.join(CURRENT_DIR, "merged_ics_attck_v2.json"))
    source_nist_controls_json = str(
        os.path.join(CURRENT_DIR, "merged_nist_controls_v1.json")
    )
    source_generated_nist_json = str(
        os.path.join(CURRENT_DIR, "attck_to_nist_controls.json")
    )

    attack = Attck(
        nested_techniques=True,
        use_config=False,
        save_config=False,
        data_path="/tmp/pyattck/data",
        enterprise_attck_json=source_enterprise_attck_json,
        pre_attck_json=source_pre_attck_json,
        mobile_attck_json=source_mobile_attck_json,
        ics_attck_json=source_ics_attck_json,
        nist_controls_json=source_nist_controls_json,
        generated_nist_json=source_generated_nist_json,
    )

    return attack


def do_verify(attack: Attck) -> None:  # noqa: C901
    print(f"Verifying mitre.json... ({MITRE_JSON_PATH})")

    errors = False

    mitre_json_contents = None
    with open(MITRE_JSON_PATH, "r") as f:
        mitre_json_contents = json.load(f)

    techs_found = []
    techs_not_found = []

    for t in attack.enterprise.techniques:
        # The enterprise.json file has sub-techniques listed twice : as techniques, and as tehcniques' subtechniques
        # We can safely ignore the subtechniques listed at the top level
        if "." in t.external_references[0].external_id:
            continue

        the_tt = None
        found = False
        for tt in mitre_json_contents["techniques"]:
            if (
                t.external_references[0].external_id == tt["id"]
                and t.name == tt["name"]
            ):
                found = True
                techs_found.append(t.external_references[0].external_id)
                the_tt = tt
        if found is False:
            techs_not_found.append(t.external_references[0].external_id)

        if not the_tt:
            continue

        subtechs_found = []
        subtechs_not_found = []

        for st in t.techniques:
            # The technique's subtechniques
            the_stt = None
            found = False
            for stt in the_tt["subtechniques"]:
                if (
                    st.external_references[0].external_id == stt["id"]
                    and st.name == stt["name"]
                ):
                    found = True
                    subtechs_found.append(st.external_references[0].external_id)
                    the_stt = stt
            if found is False:
                subtechs_not_found.append(st.external_references[0].external_id)

            subtech_tactics_found = []
            subtech_tactics_not_found = []

            if not the_stt:
                continue

            for ta in st.tactics:
                # The subtechnique's tactics
                found = False
                for stt_taa in the_stt["tactics"]:
                    if (
                        ta.external_references[0].external_id == stt_taa["id"]
                        and ta.name == stt_taa["name"]
                    ):
                        found = True
                        subtech_tactics_found.append(stt)
                if found is False:
                    subtech_tactics_not_found.append(st)

            if len(subtech_tactics_not_found):
                print(
                    f"Verification error: could not find the following tactics of subtechnique of {the_stt['id']} in mitre.json  "
                    + str(subtech_tactics_not_found)
                )
                errors = True
            if len(subtech_tactics_found) != len(the_stt["tactics"]):
                additional_tactics = list_difference(
                    the_stt["tactics"], subtech_tactics_found
                )
                print(
                    f"Verification error: the following tactics of subtechnique of {the_stt['id']} are in mitre.json and not in the reference data: {additional_tactics}"
                )
                errors = True

        if len(subtechs_not_found):
            print(
                f"Verification error: could not find the following subtechniques of {the_tt['id']} in mitre.json  "
                + str(subtechs_not_found)
            )
            errors = True
        if len(subtechs_found) != len(the_tt["subtechniques"]):
            additional_subtechs = list_difference(
                the_tt["subtechniques"], subtechs_found
            )
            print(
                f"Verification error: the following subtechniques of {the_tt['id']} are in mitre.json and not in the reference data: {additional_subtechs}"
            )
            errors = True

        tactics_found = []
        tactics_not_founds = []

        for ta in t.tactics:
            # The technique's tactics
            found = False
            for taa in the_tt["tactics"]:
                if (
                    ta.external_references[0].external_id == taa["id"]
                    and ta.name == taa["name"]
                ):
                    found = True
                    tactics_found.append(ta.external_references[0].external_id)
            if found is False:
                tactics_not_founds.append(ta.external_references[0].external_id)

        if len(tactics_not_founds):
            print(
                f"Verification error: could not find the following tactics of {the_tt['id']} in mitre.json  "
                + str(tactics_not_founds)
            )
            errors = True

        if len(tactics_found) != len(the_tt["tactics"]):
            additional_tactics = list_difference(the_tt["tactics"], tactics_found)
            print(
                f"Verification error: the following tactics of {the_tt['id']} are in mitre.json and not in the reference data: {additional_tactics}"
            )
            errors = True

    if len(techs_not_found):
        print(
            "Verification error: could not find the following techniques in mitre.json  "
            + str(techs_not_found)
        )

    if len(techs_found) != len(mitre_json_contents["techniques"]):
        additional_techs = list_difference(
            mitre_json_contents["techniques"], techs_found
        )
        print(
            f"Verification error: the following techniques are in mitre.json and not in the reference data: {additional_techs}"
        )

    if errors:
        print("Verification complete, with errors")
    else:
        print("Verification complete without errors")


def do_generate(attack: Attck) -> None:
    print("Generating mitre.json...")

    class TechniqueTmp:
        def __init__(self, id: str, name: str) -> None:
            self.id = id
            self.name = name
            self.subtechniques: List[SubTechniqueTmp] = []
            self.tactics: Set[TacticTmp] = set()

        def to_json(self) -> Any:
            return {
                "id": self.id,
                "name": self.name,
                "subtechniques": [st.to_json() for st in self.subtechniques],
                "tactics": [st.to_json() for st in self.tactics],
            }

    class SubTechniqueTmp:
        def __init__(self, id: str, name: str, parent_id: str) -> None:
            self.id = id
            self.name = name
            self.parent_id = parent_id
            self.tactics: Set[TacticTmp] = set()

        def to_json(self) -> Any:
            return {
                "id": self.id,
                "name": self.name,
                "parent_id": self.parent_id,
                "tactics": [ta.to_json() for ta in self.tactics],
            }

    class TacticTmp:
        def __init__(self, id: str, name: str) -> None:
            self.id = id
            self.name = name

        def to_json(self) -> Any:
            return {"id": self.id, "name": self.name}

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, TacticTmp):
                return False
            return self.id == other.id and self.name == other.name

        def __hash__(self) -> int:
            return hash(str(self.to_json()))

    techniques_tmp: List[TechniqueTmp] = []

    for t in attack.enterprise.techniques:
        # The enterprise.json file has sub-techniques listed twice : as techniques, and as tehcniques' subtechniques
        # We can safely ignore the subtechniques listed at the top level
        if "." in t.external_references[0].external_id:
            continue

        # The root technique
        technique = TechniqueTmp(id=t.external_references[0].external_id, name=t.name)
        techniques_tmp.append(technique)

        for st in t.techniques:
            # The technique's subtechniques
            subtechnique = SubTechniqueTmp(
                id=st.external_references[0].external_id,
                name=st.name,
                parent_id=t.external_references[0].external_id,
            )
            technique.subtechniques.append(subtechnique)

            for ta in st.tactics:
                # The subtechnique's tactics
                tactic = TacticTmp(
                    id=ta.external_references[0].external_id, name=ta.name
                )
                subtechnique.tactics.add(tactic)

        for ta in t.tactics:
            # The technique's tactics
            tactic = TacticTmp(id=ta.external_references[0].external_id, name=ta.name)
            technique.tactics.add(tactic)

    with open(MITRE_JSON_PATH, "w") as f:
        json.dump({"techniques": [t.to_json() for t in techniques_tmp]}, f)

    print(f"Techniques and tactics saved in {MITRE_JSON_PATH}")


def usage() -> None:
    print("Usage:")
    print(f"{os.path.basename(__file__)} [OPTION]")
    print("With OPTIONS being one of")
    print(
        "\t--generate   regenerate the mitre.json file, from the other json files present (default behavior)"
    )
    print(
        "\t--verify     verify the contents of the mitre.json file, based on the other json files present"
    )
    print("\t--help       print this message")


def main() -> None:
    # The script has two modes : generate the mitre.json file, or verify its
    # Both modes are based on the other json data in the current folder (for generation, or for comparison)
    generate = False
    verify = False
    if len(sys.argv) == 1 or len(sys.argv) == 2 and sys.argv[1] == "--generate":
        generate = True
    elif len(sys.argv) == 2 and sys.argv[1] == "--verify":
        verify = True
        generate = False
    elif len(sys.argv) == 2 and sys.argv[1] == "--help":
        usage()
        exit(0)
    else:
        usage()
        exit(1)

    if generate:
        attack = load_reference_mitre_data()
        do_generate(attack)
    elif verify:
        attack = load_reference_mitre_data()
        do_verify(attack)
    else:
        usage()
        exit(1)

    print("Script end")


if __name__ == "__main__":
    main()
