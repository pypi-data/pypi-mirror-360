# -*- coding: UTF-8 -*-
#! python3  # noqa E265

# ------------------------------------------------------------------------------
# Name:         Isogeo sample - Remove contacts whithin a workgroup which are not associated
# Purpose:      useful to automatically clean workgroups
# Author:       Julien Moura (@geojulien)
#
# Python:       3.6+
# ------------------------------------------------------------------------------

# ##############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from os import environ
from timeit import default_timer

# 3rd party
from dotenv import load_dotenv


# Isogeo
from isogeo_pysdk import Isogeo

# #############################################################################
# ######## Globals #################
# ##################################

# environment vars
load_dotenv(".env", override=True)
WG_TEST_UUID = environ.get("ISOGEO_WORKGROUP_TEST_UUID")


# ############################################################################
# ######## Export functions ###########
# ###########################################################################
def _meta_delete_contact(contact: dict):
    """Meta function."""
    try:
        isogeo.contact.delete(
            workgroup_id=contact.get("owner").get("_id"), contact_id=contact.get("_id")
        )

        elapsed = default_timer() - START_TIME
        time_completed_at = "{:5.2f}s".format(elapsed)
        print("{0:<30} {1:>20}".format(contact.get("name"), time_completed_at))
    except Exception as e:
        print(contact)
        logging.error(e)


# ASYNC
async def get_data_asynchronous():
    with ThreadPoolExecutor(max_workers=5, thread_name_prefix="IsogeoApi") as executor:
        # Set any session parameters here before calling `fetch`
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                _meta_delete_contact,
                # Allows us to pass in multiple arguments to `fetch`
                *(contact,),
            )
            for contact in li_wg_contacts_not_associated
        ]

        # store responses
        out_list = []
        for response in await asyncio.gather(*tasks):
            out_list.append(response)

        return out_list


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    # chronometer
    START_TIME = default_timer()

    # handle warnings
    if environ.get("ISOGEO_PLATFORM").lower() == "qa":
        import urllib3

        urllib3.disable_warnings()

    # ------------Authentication credentials ----------------
    client_id = environ.get("ISOGEO_API_USER_LEGACY_CLIENT_ID")
    client_secret = environ.get("ISOGEO_API_USER_LEGACY_CLIENT_SECRET")

    # -- Authentication and connection ---------------------------------
    # Isogeo client
    isogeo = Isogeo(
        auth_mode="user_legacy",
        client_id=client_id,
        client_secret=client_secret,
        auto_refresh_url="{}/oauth/token".format(environ.get("ISOGEO_ID_URL")),
        platform=environ.get("ISOGEO_PLATFORM", "qa"),
        lang="fr",
    )

    # getting a token
    isogeo.connect(
        username=environ.get("ISOGEO_USER_NAME"),
        password=environ.get("ISOGEO_USER_PASSWORD"),
    )

    # display elapsed time
    print("Authentication succeeded at {:5.2f}s".format(default_timer() - START_TIME))

    # get some object identifiers required for certain routes
    wg_contacts = isogeo.contact.listing(
        workgroup_id=WG_TEST_UUID, include=("count",), caching=0
    )

    # filter on contacts with count=0
    li_wg_contacts_not_associated = list(
        filter(
            lambda d: d.get("count") == 0 and "group" not in d.get("_tag"), wg_contacts
        )
    )

    # display elapsed time
    print(
        "{} contacts of workgroup {} synchronously retrieved at {:5.2f}s".format(
            len(li_wg_contacts_not_associated),
            WG_TEST_UUID,
            default_timer() - START_TIME,
        )
    )

    # -- Async loop --------------------------------------------------
    # async loop
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_data_asynchronous())
    loop.run_until_complete(future)

    # display elapsed time
    time_completed_at = "{:5.2f}s".format(default_timer() - START_TIME)
    print(
        "Cleaning complete. {} contacts deleted in {}".format(
            len(li_wg_contacts_not_associated), time_completed_at
        )
    )
