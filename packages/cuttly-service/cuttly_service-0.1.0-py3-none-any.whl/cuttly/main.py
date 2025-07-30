import requests
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, Literal
import logging
from models import (ShortenUrl,
                    CustomAliasForm,
                    CustomDomainForm,
                    CustomAliasCustomDomainForm,
                    CustomAliasNoTitleParameter,
                    CustomAliasPublicParameter,
                    LinkEditAddTagRequest,
                    LinkEditChangeAlias,
                    LinkEditChangeSourceURL,
                    LinkEditSetUniqueClicks,
                    LinkEditSetUniqueClick1440Minutes,
                    LinkEditRemoveUniqueClick,
                    LinkEditSetTitle,
                    LinkEditSetMobileRedirect,
                    LinkEditRemoveMobileRedirect,
                    LinkEditDeleteShortenedLinkSpecificEdit,
                    LinkEditSetExpirationClick,
                    LinkEditSetExpirationDate,
                    LinkEditRemoveExpiration,
                    LinkEditSetPassword,
                    LinkEditSetAbTest,
                    LinkEditSetAbcTest,
                    LinkEditTestRemove,
                    LinkAnalyticsForm,
                    LinkAnalyticsStatisticsForm,
                    LinkAnalyticsDateRangeForm,
                    TraiSMSDomain,
                    TraiSMSDomainCustomAlias)

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

class CuttlyClient:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.base_url = os.getenv("BASE_URL")
        self.headers = {"Content-Type": "application/json"}

    def fetch_data(self, params: dict):

        try:
            params['key'] = self.api_key
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            return response
        except:
            logging.error(f"HTTPError: {response.status_code} - {response.text}")
            return response

    def shorten_url(self, short: str):

        parameters = ShortenUrl(
            short=short
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def shorten_url_custom_alias(self, short: str, name: str):

        parameters = CustomAliasForm(
            short=short,
            name=name
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }


    def shorten_url_custom_domain(self, short: str, userDomain: int):

        parameters = CustomDomainForm(
            short=short,
            userDomain=userDomain
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }


    def shorten_url_custom_alias_custom_domain(self, short: str, name: str, userDomain: int):

        parameters = CustomAliasCustomDomainForm(
            short=short,
            name=name,
            userDomain=userDomain
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }


    def shorten_url_no_title_parameter(self, short: str, noTitle: int):

        parameters = CustomAliasNoTitleParameter(
            short=short,
            noTitle=noTitle
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def shorten_url_public_parameter(self, short: str, public: int):

        parameters = CustomAliasPublicParameter(
            short=short,
            public=public
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def shorten_url_trai_sms_domain(self, short: str, userDomain: int):

        parameters = TraiSMSDomain(
            short=short,
            userDomain=userDomain
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def shorten_url_trai_sms_domain_custom_alias(self, short: str, userDomain: int, name = str):

        parameters = TraiSMSDomainCustomAlias(
            short=short,
            userDomain=userDomain,
            name=name
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def link_edit_add_tag(self, edit: str, tag: Optional[str] = None):

        parameters = LinkEditAddTagRequest(
            edit=edit,
            tag=tag
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def link_edit_change_alias(self, edit: str, name: Optional[str] = None):
        parameters = LinkEditChangeAlias(
            edit=edit,
            name=name
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def link_edit_change_source_url(self, edit: str, source: str):

        parameters = LinkEditChangeSourceURL(
            edit=edit,
            source=source
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }


    def link_edit_set_unique_clicks(self, edit: str, unique: Literal[0,1]):

        parameters = LinkEditSetUniqueClicks(
            edit=edit,
            unique=unique
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def link_edit_set_unique_clicks_1440_minutes(self, edit: str, unique: int):

        parameters = LinkEditSetUniqueClick1440Minutes(
            edit=edit,
            unique=unique
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def link_edit_remove_unique_click(self, edit: str, unique: Literal[0,1]):

        parameters = LinkEditRemoveUniqueClick(
            edit=edit,
            unique=unique
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def link_edit_set_title(self, edit: str, title: str):

        parameters = LinkEditSetTitle(
            edit=edit,
            title=title
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }


    def link_edit_set_mobile_redirect(self, edit: str, mobile: str, destinationURL: str):

        parameters = LinkEditSetMobileRedirect(
            edit=edit,
            mobile=mobile,
            destination=destinationURL
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def link_edit_remove_mobile_redirect(self, edit: str, mobile: str):

        parameters = LinkEditRemoveMobileRedirect(
            edit=edit,
            mobile=mobile
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def edit_link_delete_shortened_link_specific_edit(self, edit: str, delete: int):

        parameters = LinkEditDeleteShortenedLinkSpecificEdit(
            edit=edit,
            delete=delete
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def edit_link_set_expiration_click(self, edit: str, expire: int, expireCond: str, expireRedirect: str, expireUnique: int):

        parameters = LinkEditSetExpirationClick(
            edit=edit,
            expire=expire,
            expireCond=expireCond,
            expireRedirect=expireRedirect,
            expireUnique=expireUnique
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def edit_link_set_expiration_date(self, edit: str, expire: int, expireCond: str, expireRedirect: str, expireUnique: int):

        parameters = LinkEditSetExpirationDate(
            edit=edit,
            expire=expire,
            expireCond=expireCond,
            expireRedirect=expireRedirect,
            expireUnique=expireUnique
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def edit_link_remove_expiration(self, edit: str, expire: int, expireCond: int ):

        parameters = LinkEditRemoveExpiration(
            edit=edit,
            expire=expire,
            expireCond=expireCond
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def edit_link_set_password(self, edit: str, password: int):

        parameters = LinkEditSetPassword(
            edit=edit,
            password=password
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def edit_link_set_ab_test(self, edit: str, abtest: str, abtest_b: int, abtest_bvariation: str):

        parameters = LinkEditSetAbTest(
            edit=edit,
            abtest=abtest,
            abtest_b=abtest_b,
            abtest_bvariation=abtest_bvariation
        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def edit_link_set_abc_test(self, edit: str, abtest: int, abtest_b: int, abtest_bvariation: str, abtest_c: int, abtest_cvariation: str):

        parameters = LinkEditSetAbcTest(
            edit=edit,
            abtest=abtest,
            abtest_b=abtest_b,
            abtest_bvariation=abtest_bvariation,
            abtest_c=abtest_c,
            abtest_cvariation=abtest_cvariation

        )
        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }

    def edit_link_abc_test_remove(self, edit: str, abtest: int):

        parameters = LinkEditTestRemove(
            edit=edit,
            abtest=abtest
        )

        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }


    def link_analytics(self, edit: str, date_from, date_to):

        parameters = LinkAnalyticsForm(
            edit=edit,
            date_from=date_from,
            date_to=date_to
        )

        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }


    def link_analytics_statistics(self, edit: str, stats: str):

        parameters = LinkAnalyticsStatisticsForm(
            edit=edit,
            stats=stats
        )

        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }


    def link_analytics_date_range(self, stats: str, date_from, date_to):

        parameters = LinkAnalyticsDateRangeForm(
            stats=stats,
            date_from=date_from,
            date_to=date_to
        )

        params = parameters.model_dump(exclude_none=True)

        response = self.fetch_data(params)

        if response.status_code == 200:
            return {
                "success": True,
                "message": "True",
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "message": "False",
                "data": response.json()
            }


ctl = CuttlyClient()
request = ctl.shorten_url("https://chatgpt.com/c/tttttttttttttt")
#request12 = ctl.link_edit_add_tag("https://cutt.ly/vrYxXj7L","asda3sd")
##request = ctl.link_edit_change_alias("https://cutt.ly/4v2222f","332223")
print(request)