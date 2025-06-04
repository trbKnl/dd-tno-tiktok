"""
TikTok

This module contains an example flow of a TikTok data donation study

Assumptions:
It handles DDPs in the english language with filetype txt.
"""

from typing import Any, Tuple
import logging
import io
import re

import pandas as pd

import port.api.props as props
import port.api.d3i_props as d3i_props
import port.helpers.extraction_helpers as eh
import port.helpers.port_helpers as ph
import port.helpers.validate as validate
from port.platforms.flow_builder import FlowBuilder

from port.helpers.validate import (
    DDPCategory,
    DDPFiletype,
    Language,
)

logger = logging.getLogger(__name__)

DDP_CATEGORIES = [
    DDPCategory(
        id="json_en",
        ddp_filetype=DDPFiletype.JSON,
        language=Language.EN,
        known_files=[
            "user_data_tiktok.json"
        ],
    ),
    DDPCategory(
        id="txt_en",
        ddp_filetype=DDPFiletype.TXT,
        language=Language.EN,
        known_files=[
            "Transaction History.txt",
            "Most Recent Location Data.txt",
            "Comments.txt",
            "Purchases.txt",
            "Share History.txt",
            "Favorite Sounds.txt",
            "Searches.txt",
            "Login History.txt",
            "Favorite Videos.txt",
            "Favorite HashTags.txt",
            "Hashtag.txt",
            "Location Reviews.txt",
            "Favorite Effects.txt",
            "Following.txt",
            "Status.txt",
            "Browsing History.txt",
            "Like List.txt",
            "Follower.txt",
            "Watch Live settings.txt",
            "Go Live settings.txt",
            "Go Live History.txt",
            "Watch Live History.txt",
            "Profile Info.txt",
            "Autofill.txt",
            "Post.txt",
            "Block List.txt",
            "Settings.txt",
            "Customer support history.txt",
            "Communication with shops.txt",
            "Current Payment Information.txt",
            "Returns and Refunds History.txt",
            "Product Reviews.txt",
            "Order History.txt",
            "Vouchers.txt",
            "Saved Address Information.txt",
            "Order dispute history.txt",
            "Product Browsing History.txt",
            "Shopping Cart List.txt",
            "Direct Messages.txt",
            "Off TikTok Activity.txt",
            "Ad Interests.txt",
        ],
    ),
]



def read_tiktok_file(tiktok_file: str) -> dict[Any, Any] | list[Any]:

    buf = eh.extract_file_from_zip(tiktok_file, "user_data_tiktok.json")
    out = eh.read_json_from_bytes(buf)
    if not out:
        out = eh.read_json_from_file(tiktok_file)

    return out


 
def watch_history_to_df(tiktok_zip) -> pd.DataFrame:

    d = read_tiktok_file(tiktok_zip)
    datapoints = []
    out = pd.DataFrame()

    try: 
        history = d["Your Activity"]["Watch History"]["VideoList"] # pyright: ignore
        for item in history:
            datapoints.append((
                item.get("Date", None),
                item.get("Link", None)
            ))

        out = pd.DataFrame(datapoints, columns=["Date", "Url"]) # pyright: ignore
    except Exception as e:
        logger.error("Could not extract tiktok history: %s", e)

    return out


def browsing_history_to_df(file: str, validation) -> pd.DataFrame:

    out = pd.DataFrame()

    if file == "/file-input/user_data_tiktok.json":
        out = watch_history_to_df(file)
    else:
        if validation.current_ddp_category != None:
            if validation.current_ddp_category.id == "json_en":
                out = watch_history_to_df(file)

            if validation.current_ddp_category.id == "txt_en":
                try:
                    b = eh.extract_file_from_zip(file, "Watch History.txt")
                    b = io.TextIOWrapper(b, encoding='utf-8')
                    text = b.read()

                    pattern = re.compile(r"^Date: (.*?)\nLink: (.*?)$", re.MULTILINE)
                    matches = re.findall(pattern, text)
                    out = pd.DataFrame(matches, columns=["Time and Date", "Video watched"]) # pyright: ignore

                except Exception as e:
                    logger.error(e)

    return out

###########################################
# shares


def share_history_to_df_txt(tiktok_zip: str):

    out = pd.DataFrame()

    try:
        b = eh.extract_file_from_zip(tiktok_zip, "Share History.txt")
        b = io.TextIOWrapper(b, encoding='utf-8')
        text = b.read()

        pattern = re.compile(r"^Date: (.*?)\nShared Content: (.*?)\nLink: (.*?)\nMethod: (.*?)$", re.MULTILINE)
        matches = re.findall(pattern, text)
        out = pd.DataFrame(matches, columns=["Time and date", "Shared content", "Link", "Method"]) # pyright: ignore

    except Exception as e:
        logger.error(e)

    return out


def share_history_to_df_json(tiktok_zip: str) -> pd.DataFrame:

    d = read_tiktok_file(tiktok_zip)
    datapoints = []
    out = pd.DataFrame()

    try:  # pyright: ignore
        history = d["Your Activity"]["Share History"]["ShareHistoryList"] #pyright: ignore
        for item in history:
            datapoints.append((
                item.get("Date", None), 
                item.get("SharedContent", None),
                item.get("Link", None),
                item.get("Method", None)
            ))

        out = pd.DataFrame(datapoints, columns=["Date", "Shared Content", "Url", "Method"]) # pyright: ignore
    except Exception as e:
        logger.error("Could not extract: %s", e)

    return out



def share_history_to_df(file: str, validation) -> pd.DataFrame:

    out = pd.DataFrame()

    if file == "/file-input/user_data_tiktok.json":
        out = share_history_to_df_json(file)
    else:
        if validation.current_ddp_category != None:
            if validation.current_ddp_category.id == "json_en":
                out = share_history_to_df_json(file)

            if validation.current_ddp_category.id == "txt_en":
                out = share_history_to_df_txt(file)

    return out


###########################################
# likes

def like_list_to_df_txt(tiktok_zip: str):

    out = pd.DataFrame()

    try:
        b = eh.extract_file_from_zip(tiktok_zip, "Like List.txt")
        b = io.TextIOWrapper(b, encoding='utf-8')
        text = b.read()

        pattern = re.compile(r"^Date: (.*?)\nLink: (.*?)$", re.MULTILINE)
        matches = re.findall(pattern, text)
        out = pd.DataFrame(matches, columns=["Time and date", "Link"]) # pyright: ignore

    except Exception as e:
        logger.error(e)

    return out


def like_list_to_df_json(tiktok_zip: str) -> pd.DataFrame:

    d = read_tiktok_file(tiktok_zip)
    datapoints = []
    out = pd.DataFrame()

    try: 
        history = d["Your Activity"]["Like List"]["ItemFavoriteList"] # pyright: ignore
        for item in history:
            datapoints.append((
                item.get("date", ""),
                item.get("link", ""),
            ))

        out = pd.DataFrame(datapoints, columns=["Date", "Url"]) # pyright: ignore
    except Exception as e:
        logger.error("Could not extract: %s", e)

    return out


def like_list_to_df(file: str, validation) -> pd.DataFrame:

    out = pd.DataFrame()

    if file == "/file-input/user_data_tiktok.json":
        out = like_list_to_df_json(file)
    else:
        if validation.current_ddp_category != None:
            if validation.current_ddp_category.id == "json_en":
                out = like_list_to_df_json(file)

            if validation.current_ddp_category.id == "txt_en":
                out = like_list_to_df_txt(file)

    return out


####################################################

def extraction(tiktok_zip: str, validation) -> Tuple[list[d3i_props.PropsUIPromptConsentFormTableViz], bool]:
    browsing_history = browsing_history_to_df(tiktok_zip, validation)
    is_browsing_history_empty = browsing_history.empty

    tables = [
        d3i_props.PropsUIPromptConsentFormTableViz(
            id="tiktok_video_browsing_history",
            data_frame=browsing_history,
            title=props.Translatable({
                "en": "Watch history", 
                "nl": "Kijkgeschiedenis"
            }),
            description=props.Translatable({
                "en": "The table below indicates exactly which TikTok videos you have watched and when that was.",
                "nl": "De tabel hieronder geeft aan welke TikTok video's je precies hebt bekeken en wanneer dat was.",
            }),
            visualizations=[]
        ),
        d3i_props.PropsUIPromptConsentFormTableViz(
            id="tiktok_share_history",
            data_frame=share_history_to_df(tiktok_zip, validation),
            title=props.Translatable({
                "en": "Share history", 
                "nl": "Deelgeschiedenis"
            }),
            description=props.Translatable({
                "en": "The table below indicates exactly which TikTok videos you have shared and when that was.",
                "nl": "De tabel hieronder geeft aan welke TikTok video's je precies hebt gedeeld en wanneer dat was."
            }),
            visualizations=[]
        ),
        d3i_props.PropsUIPromptConsentFormTableViz(
            id="tiktok_like_list",
            data_frame=like_list_to_df(tiktok_zip, validation),
            title=props.Translatable({
                "en": "Like history", 
                "nl": "Likegeschiedenis"
            }),
            description=props.Translatable({
                "en": "The table below indicates exactly which TikTok videos you have liked and when that was.",
                "nl": "De tabel hieronder geeft aan welke TikTok video's je precies hebt geliked en wanneer dat was.",
            }),
            visualizations=[]
        ),
    ]

    tables_to_render = [table for table in tables if table.data_frame is not None and not table.data_frame.empty]
    return (tables_to_render, is_browsing_history_empty)


class TikTokFlow(FlowBuilder):
    def __init__(self, session_id: int):
        super().__init__(session_id, "TikTok")
        
    def generate_file_prompt(self):
        return ph.generate_file_prompt("application/zip, application/json, text/plain")

    def validate_file(self, file):
        validation = validate.validate_zip(DDP_CATEGORIES, file)
        if file == "/file-input/user_data_tiktok.json":
            validation.set_current_status_code_by_id(0)

        return validation

    def extract_data(self, file_value, validation):
        return extraction(file_value, validation)


def process(session_id):
    flow = TikTokFlow(session_id)
    return flow.start_flow()
