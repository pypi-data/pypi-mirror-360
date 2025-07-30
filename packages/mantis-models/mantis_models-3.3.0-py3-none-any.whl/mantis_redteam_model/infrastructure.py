# -*- coding: utf-8 -*-
from enum import Enum

from pydantic import BaseModel


class InfrastructureTypeEnum(str, Enum):
    c2_http = "C2_http"
    c2_https = "C2_https"
    c2_proxy = "C2_proxy"
    nginx_server = "nginx_server"
    winrm_client = "winrm_client"
    upload_server = "upload_server"
    ftp_upload_server = "ftp_upload_server"
    ldap = "LDAP"
    webdav_server = "webdav_server"
    chisel_server = "chisel_server"
    ntlmrelay_server = "ntlmrelay_server"


class InfrastructureTypeName(BaseModel):
    value: InfrastructureTypeEnum
