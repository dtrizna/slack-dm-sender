import argparse
import sys
import logging
import json
from json.decoder import JSONDecodeError

from slack import WebClient
from slack.errors import SlackApiError


def slack_connect(token):
        slack = WebClient(token=token)
        try:
                api_test = slack.api_test()
                return slack
        except SlackApiError as e:
                # SlackApiError is raised if api_test.data["ok"] is False
                logging.error(" [-] Error when connecting to Slack...")
                logging.error(f" {e.response['error']}")
                logging.error(" For addition info run script with debug [-d] flag.")
                sys.exit(1)


def read_users(args):
        userlist = []
        if args.users:
                userlist.extend([x.strip() for x in args.users.split(",")])
        elif args.userFile:
                with open(args.userFile) as f2:
                        lines = f2.readlines()
                        for line in lines:
                                if "\\" in line:
                                        userlist.append(line.split("\\")[1].strip())
                                elif "@" in line:
                                        userlist.append(line.split("@")[0].strip())
                                else:
                                        userlist.append(line.strip())
        else:
                print("[-] Please specify users with --users or --userFile options.")
                sys.exit(1)
        return userlist


def read_message(args):
        if args.message:
                message = args.message
        elif args.messageFile:
                with open(args.messageFile) as f3:
                        message = f3.read()
        elif args.queryOnly:
                return None
        else:
                logging.error(" [-] Please specify message to send with --message or --messageFile options.")
                sys.exit(1)
        return message


def send_message(slack, USER, MSG, id=False):
        if not id:
                USER = f"@{USER}"
        try:
                try:
                        # if message is from block kit
                        slack.chat_postMessage(channel=USER, blocks=json.loads(MSG)["blocks"])
                except JSONDecodeError:
                        slack.chat_postMessage(channel=USER,text=MSG)
                
        except SlackApiError as e:
                logging.error(f" [-] Error when sending message to {USER}: {e.response['error']}. For debug info run script with -d flag.")



def main():
        parser = argparse.ArgumentParser(
                description="Sends message to a Slack user[s] given API token.",
                usage=f"""
\tpython3 {sys.argv[0]} -st .slack_token -m \"Hello there! :joy:\" -u dtrizna,testuser,admin
\tpython3 {sys.argv[0]} -st .slack_token -mF message.txt -uF user.list
""")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-m","--message", help="Message to send.")
        group.add_argument("-mF", "--messageFile", help="Message to send taken from file.")

        group2 = parser.add_mutually_exclusive_group()
        group2.add_argument("-u", "--users", help="Comma separated user list whom to send message.")
        group2.add_argument("-uF", "--userFile", help="User list taken from file (username per line) whom to send message.")

        parser.add_argument("-st", "--slackToken", help="File with Slack token inside.")
        
        parser.add_argument("-v", "--verbose", action="store_true")
        parser.add_argument("-d", "--debug", action="store_true", help="Slack provides DEBUG logging for troubleshooting.")
        
        args = parser.parse_args()

        if args.debug: # Debug?
                logging.basicConfig(level=logging.DEBUG)

        # Instantiate Slack
        if args.slackToken:
                with open(args.slackToken) as f:
                        slack_token = f.read()
                slack = slack_connect(slack_token)
        else:
                print("\n[!] Please provide either Slack token or Okta token with --queryOnly!\n")
                sys.exit(1)

        userlist = read_users(args)
        message = read_message(args)

        for i,user in enumerate(userlist):
                print(f"[+] Sending message to @{user}.")
                send_message(slack, user, message)


if __name__ == "__main__":
        main()
