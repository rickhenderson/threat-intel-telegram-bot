#!/usr/bin/env python
from dotenv import load_dotenv
import vt
from dataclasses import dataclass


@dataclass
class FileMetadata:
    name: str
    sha256: str
    total_votes: str
    creation_date: int  # UTC timestamp
    
#file_meta = FileMetadata(
#    name="cobalt",
#    sha256="",
#    total_votes="0",
#    creation_date=0
#)

load_dotenv()


def get_total_votes_by_hash(fileSHA256hash):
    # client = vt.Client(VIRUS_TOTAL_TOKEN)
    #file = client.get_object(f"/files/{fileSHA256hash}")
    result = "nyi"
    return result

def get_file_name_from_vt(fileSHA256hash):
    client = vt.Client(VIRUS_TOTAL_TOKEN)
    file = client.get_object(f"/files/{fileSHA256hash}")
    return file.names

