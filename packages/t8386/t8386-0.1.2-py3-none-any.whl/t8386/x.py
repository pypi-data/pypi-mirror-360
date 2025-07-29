import binascii
import requests

import json

import random

import secrets

from t8386.logger import Logger


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"

SEC_CH_UA = '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"'

SEC_CH_UA_PLATFORM = '"Windows"'


class AppBindConfig:
    # Example url: "https://twitter.com/i/oauth2/authorize?response_type=code&client_id=d1E1aFNaS0xVc2swaVhFaVltQlY6MTpjaQ&redirect_uri=https%3A%2F%2Fearn.taker.xyz%2Fbind%2Fx&scope=tweet.read+users.read+follows.read&state=state&code_challenge=challenge&code_challenge_method=plain"
    """Class to handle app binding"""

    def __init__(self, client_id, redirect_uri, scope, state=None, code_challenge=None, code_challenge_method="S256"):
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.state = state or secrets.token_urlsafe(16)
        self.code_challenge = code_challenge
        self.code_challenge_method = code_challenge_method

    def copy(self):
        """Create a copy of the AppBindConfig instance"""
        return AppBindConfig(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            state=self.state,
            code_challenge=self.code_challenge,
            code_challenge_method=self.code_challenge_method
        )

class Twitter:
    """Class to handle Twitter API interactions"""

    @staticmethod
    def generate_csrf_token(size=16):
        """Generate a random CSRF token"""

        data = random.getrandbits(size * 8).to_bytes(size, "big")

        return binascii.hexlify(data).decode()

    @staticmethod
    def get_twitter_headers(ct0, auth_token):

        return {
            "accept": "*/*",
            "accept-language": "en;q=0.9",
            "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
            "content-type": "application/json",
            "origin": "https://x.com",
            "referer": "https://x.com/",
            "sec-ch-ua": SEC_CH_UA,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": SEC_CH_UA_PLATFORM,
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-twitter-active-user": "yes",
            "x-twitter-auth-type": "OAuth2Session",
            "x-twitter-client-language": "en",
            "x-csrf-token": ct0,
            "user-agent": USER_AGENT,
            "cookie": f"ct0={ct0}; auth_token={auth_token}; twid=u%3D801990002",
        }

    @staticmethod
    def twitter_session_instance(twitter_auth_token, proxy=None):
        twitter_session = requests.Session()

        ct0 = Twitter.generate_csrf_token()

        cookies = {
            "auth_token": twitter_auth_token,
            "ct0": ct0,
            "twid": "u%3D801990002",
        }

        for domain in [".x.com", ".twitter.com"]:

            for key, value in cookies.items():

                twitter_session.cookies.set(key, value, domain=domain)

        twitter_headers = Twitter.get_twitter_headers(ct0, twitter_auth_token)

        # Set proxy for Twitter session

        if proxy:
            twitter_session.proxies = {"http": proxy, "https": proxy}

        return twitter_session, twitter_headers

    @staticmethod
    def check_x_token(twitter_auth_token, proxy=None):
        """Check if the provided X token is valid"""

        twitter_session, twitter_headers = Twitter.twitter_session_instance(
            twitter_auth_token, proxy)
        if not twitter_session:
            Logger.log_error(f"❌ Failed to create Twitter session!")
            return False

        verify_result = Twitter.verify_twitter_account(
            twitter_session, twitter_headers, twitter_auth_token
        )

        if verify_result == "locked":
            Logger.log_warning(f"🔒 Twitter account {twitter_auth_token} is temporarily locked!")
            return False

        elif verify_result is True:
            Logger.log_success(f"♾️ Twitter account {twitter_auth_token} is valid!")
            return True


    def verify_twitter_account(session, headers, twitter_token=None):

        viewer_url = "https://api.x.com/graphql/UhddhjWCl-JMqeiG4vPtvw/Viewer"

        features = {
            "rweb_tipjar_consumption_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
        }

        field_toggles = {"isDelegate": False, "withAuxiliaryUserLabels": False}

        variables = {"withCommunitiesMemberships": True}

        params = {
            "variables": json.dumps(variables),
            "features": json.dumps(features),
            "fieldToggles": json.dumps(field_toggles),
        }

        try:

            response = session.get(viewer_url, headers=headers, params=params)

            if response.status_code == 200:

                data = response.json()

                # Check for locked account

                if "errors" in data:

                    for err in data["errors"]:

                        if "temporarily locked" in err.get("message", ""):

                            return "locked"

                if "data" in data and "viewer" in data["data"]:

                    username = data["data"]["viewer"]["user_results"]["result"]["legacy"][
                        "screen_name"
                    ]

                    Logger.log_success(f"♾️ Twitter account: @{username}")

                    return True

                else:

                    Logger.log_error(f"❌ Invalid Twitter response structure: {response.text}")


            elif response.status_code == 401:

                Logger.log_error(f"💀 Dead Twitter Token!")

            else:

                Logger.log_error(f"❌ Twitter verification failed with status={response.status_code} - {response.reason} - {response.text}")

        except Exception as e:

            Logger.log_error(f"❌ Error during Twitter verification: {str(e)}")

        return False

    @staticmethod
    def bind(app_bind_config: AppBindConfig, auth_token, proxy=None):
        """Connect to X with the provided proxy"""

        # app_bind_config = AppBindConfig(
        #     client_id="d1E1aFNaS0xVc2swaVhFaVltQlY6MTpjaQ",
        #     redirect_uri="https://earn.taker.xyz/bind/x",
        #     scope="tweet.read users.read follows.read",
        #     code_challenge="challenge",
        #     code_challenge_method="plain",
        #     state="state"
        # )

        twitter_session, twitter_headers = Twitter.twitter_session_instance(
            auth_token, proxy)
        if not twitter_session:
            Logger.log_error(f"❌ Failed to create Twitter session!")
            return None

        try:

            auth_url = f"https://x.com/i/api/2/oauth2/authorize"

            auth_params = {
                "response_type": "code",
                "client_id": app_bind_config.client_id,
                "redirect_uri": app_bind_config.redirect_uri,
                "scope": app_bind_config.scope,
                "state": app_bind_config.state,
                "code_challenge": app_bind_config.code_challenge,
                "code_challenge_method": app_bind_config.code_challenge_method,
            }

            auth_headers = twitter_headers.copy()

            auth_headers.update(
                {
                    "x-twitter-active-user": "yes",
                    "x-twitter-auth-type": "OAuth2Session",
                    "x-twitter-client-language": "en",
                    "x-client-transaction-id": Twitter.generate_csrf_token(32),
                }
            )

            auth_response = twitter_session.get(
                auth_url, params=auth_params, headers=auth_headers
            )

            if auth_response.status_code != 200:

                Logger.log_error(f"❌ Failed to get auth code: {auth_response.status_code}")

                # print(f"{Fore.YELLOW}Response: {auth_response.text[:200]}...{Style.RESET_ALL}")

                return None

            auth_data = auth_response.json()

            if "auth_code" not in auth_data:

                Logger.log_error(f"❌ No auth code in response: {json.dumps(auth_data)[:200]}...")

                return None

            auth_code = auth_data["auth_code"]
            Logger.log_success(f"✅ Auth code received: {auth_code}")

            approve_url = "https://x.com/i/api/2/oauth2/authorize"

            approve_headers = auth_headers.copy()

            approve_headers.update(
                {
                    "content-type": "application/x-www-form-urlencoded",
                    "x-client-transaction-id": Twitter.generate_csrf_token(32),
                }
            )

            approve_data = {"approval": "true", "code": auth_code}

            approve_response = twitter_session.post(
                approve_url, headers=approve_headers, data=approve_data
            )

            if approve_response.status_code != 200:

                Logger.log_error(f"❌ Failed to approve auth code with status={approve_response.status_code}: {approve_response.reason} - {approve_response.text[:200]}...")

                return None

            Logger.log_success(f"✅ Auth code approved successfully!")
            # Now we can exchange the auth code for an access token

            callback_params = {"state": app_bind_config.state, "code": auth_code}

            callback_url = f"{app_bind_config.redirect_uri}?{requests.compat.urlencode(callback_params)}"

            Logger.log_info(f"🔗 Redirecting to: {callback_url}")

            return {
                'code': auth_code,
                'callback_url': callback_url,
            }

        except Exception as e:
            Logger.log_error(f"❌ Error during binding: {str(e)}")
            return None


# if __name__ == "__main__":
#     auth_tokens = [
#         'c5e508ad80e0059ca45b7079da0266f919f4d4f3',
#         '96105379cffd6802d4b4a02f8e9f22a059892872',
#         'cf3054ec9f4c89d2f1caddd3c671459a2226240b',
#     ]
#     proxy = "http://mitomtoan26:mitomtoan26@14.188.66.130:13029"

#     for auth_token in auth_tokens:
#         # print(f"{Fore.YELLOW}🔗 Checking auth token: {auth_token}{Style.RESET_ALL}")

#         check_x_token(auth_token, proxy)
            # print(f"{Fore.GREEN}✅ Auth token is valid!{Style.RESET_ALL}")
        # else:
        #     print(f"{Fore.RED}❌ Auth token is invalid!{Style.RESET_ALL}")

    # app_bind_config = AppBindConfig(
    #     client_id="d1E1aFNaS0xVc2swaVhFaVltQlY6MTpjaQ",
    #     redirect_uri="https://earn.taker.xyz/bind/x",
    #     scope="tweet.read users.read follows.read",
    #     code_challenge="challenge",
    #     code_challenge_method="plain",
    #     state="state"
    # )

    # bind(app_bind_config=app_bind_config, auth_token=auth_token, proxy=proxy)
