# -*- coding: utf-8 -*-
from enum import Enum
from typing import List

from pydantic import BaseModel


# Enum pour les types de signature (les différentes plateformes de SIEM ou NIDS)
class SignatureType(str, Enum):
    elk_lucene = "elk_lucene"
    elk_esql = "elk_esql"
    azure_kql = "azure_kql"
    splunk = "splunk"
    graylog = "graylog"
    snort = "snort"
    suricata = "suricata"


class ImplementationType(str, Enum):
    sh = "sh"
    powershell = "powershell"


# Modèle représentant une signature spécifique pour un type donné
class SignatureModel(BaseModel):
    signature_type: SignatureType  # Type de signature (par exemple, elk_lucene, splunk)
    signature: str  # Règle ou expression régulière spécifique pour la signature


# Modèle représentant une implémentation contenant plusieurs signatures
class Implementation(BaseModel):
    id: str  # ID unique de règle
    implementation_type: ImplementationType  # Nom de l'implémentation
    signatures: List[SignatureModel]  # Liste de signatures dans cette implémentation
    log_collectors_required: List[
        str
    ]  # List des log connectors requis pour cette implémentation


# Modèle représentant une signature avec une description et une liste de signatures associées
class Signature(BaseModel):
    attack_reference_id: str  # Référence à l'id de l'attaque (cron, registry_run, etc.)
    implementations: List[
        Implementation
    ]  # Liste des implémentations spécifiques à différents types de systèmes
