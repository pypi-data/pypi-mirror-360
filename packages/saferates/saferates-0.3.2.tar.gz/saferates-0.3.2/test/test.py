import json
import os
from saferates import (
    SaferatesAPI, SaferatesChannels, SaferatesFriends, SaferatesGuilds,
    SaferatesEmbeds, SaferatesWebhooks, SaferatesReminders, SaferatesBackup,
    SaferatesPolls, SaferatesInvites, SaferatesHistory, SaferatesAntiSpam,
    SaferatesExport, SaferatesStickers, SaferatesPresence, SaferatesRoles,
    SaferatesEmojis, SaferatesNitro, SaferatesAudit, SaferatesVoice,
    SaferatesModerator, SaferatesWelcome, SaferatesCommands,
    saferates_pretty_json
)

CONFIG_FILE = "config.json"

def load_token():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                token = cfg.get("token")
                if token:
                    print("Loaded user token from config file.")
                    return token
        except (json.JSONDecodeError, ValueError):
            print("Warning: Config file corrupted or empty. Re-entering token.")
    token = input("Enter your Discord user token: ").strip()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"token": token}, f)
    print("Saved user token to config file.")
    return token

def prompt(msg, required=True):
    val = input(msg)
    while required and not val.strip():
        val = input(msg)
    return val.strip()

def pause():
    input("Press Enter to continue...")

def menu_header(title):
    print(f"\n{'='*10} {title} {'='*10}")

def menu_account(api):
    menu_header("Account/Friends")
    friends = SaferatesFriends(api)
    print("1. Add friend\n2. Remove friend\n3. Block user\n4. Unblock user\n5. Export friends list\n6. Back")
    choice = prompt("Select option: ")
    if choice == "1":
        print(friends.saferates_add(prompt("User ID: ")))
    elif choice == "2":
        print(friends.saferates_remove(prompt("User ID: ")))
    elif choice == "3":
        print(friends.saferates_block(prompt("User ID: ")))
    elif choice == "4":
        print(friends.saferates_unblock(prompt("User ID: ")))
    elif choice == "5":
        export = SaferatesExport(api)
        path = export.saferates_export_friends()
        print(f"Exported friends to {path}")
    pause()

def menu_guilds(api):
    menu_header("Guilds")
    guilds = SaferatesGuilds(api)
    print("1. List my guilds\n2. Leave guild\n3. Mass leave\n4. Backup guild\n5. Back")
    choice = prompt("Select option: ")
    if choice == "1":
        print(saferates_pretty_json(guilds.saferates_list()))
    elif choice == "2":
        print(guilds.saferates_leave(prompt("Guild ID: ")))
    elif choice == "3":
        gids = prompt("Guild IDs (comma-separated): ").split(",")
        print(guilds.saferates_mass_leave([g.strip() for g in gids if g.strip()]))
    elif choice == "4":
        backup = SaferatesBackup(api)
        print(backup.saferates_backup_guild(prompt("Guild ID: ")))
    pause()

def menu_channels(api):
    menu_header("Channels")
    channels = SaferatesChannels(api)
    print("1. Create channel\n2. Edit channel\n3. Delete channel\n4. Back")
    choice = prompt("Select option: ")
    if choice == "1":
        print(channels.saferates_create(
            prompt("Guild ID: "), prompt("Channel name: "),
            int(prompt("Channel type (0=text,2=voice,4=category): "))
        ))
    elif choice == "2":
        cid = prompt("Channel ID: ")
        name = prompt("New name: ", required=False)
        topic = prompt("New topic: ", required=False)
        fields = {}
        if name: fields["name"] = name
        if topic: fields["topic"] = topic
        print(channels.saferates_edit(cid, **fields))
    elif choice == "3":
        print(channels.saferates_delete(prompt("Channel ID: ")))
    pause()

def menu_messaging(api):
    menu_header("Messaging")
    channels = SaferatesChannels(api)
    embeds = SaferatesEmbeds(api)
    print("1. Send message\n2. Send embed\n3. Send sticker\n4. Send file (attachment)\n5. Back")
    choice = prompt("Select option: ")
    if choice == "1":
        print(channels.saferates_send_message(
            prompt("Channel ID: "), prompt("Content: ")
        ))
    elif choice == "2":
        title = prompt("Embed title: ")
        desc = prompt("Embed description: ")
        color = int(prompt("Color hex (e.g. 0x5865F2): "), 16)
        embed = embeds.saferates_build_embed(title=title, description=desc, color=color)
        print(embeds.saferates_send_embed(prompt("Channel ID: "), embed))
    elif choice == "3":
        stickers = SaferatesStickers(api)
        print(stickers.saferates_send_sticker(
            prompt("Channel ID: "), prompt("Sticker ID: ")
        ))
    elif choice == "4":
        path = prompt("Path to file: ")
        print(channels.saferates_send_attachment(
            prompt("Channel ID: "), path
        ))
    pause()

def menu_dm(api):
    menu_header("Direct Messages / Anti-Spam")
    from saferates.dms import SaferatesDMs
    dms = SaferatesDMs(api)
    antispam = SaferatesAntiSpam(api)
    print("1. Send DM\n2. Bulk DM\n3. Prune spam DMs\n4. Delete DM channel\n5. Back")
    choice = prompt("Select option: ")
    if choice == "1":
        print(dms.send_dm(prompt("User ID: "), prompt("Message: ")))
    elif choice == "2":
        ids = prompt("User IDs (comma-separated): ").split(",")
        print(dms.bulk_dm([i.strip() for i in ids if i.strip()], prompt("Message: ")))
    elif choice == "3":
        print(antispam.saferates_block_nonfriend_dms())
    elif choice == "4":
        print(dms.delete_dm_channel(prompt("DM Channel ID: ")))
    pause()

def menu_webhook():
    menu_header("Webhooks")
    webhooks = SaferatesWebhooks()
    print("1. Send webhook\n2. Edit webhook\n3. Delete webhook\n4. Back")
    choice = prompt("Select option: ")
    url = None
    if choice in "123":
        url = prompt("Webhook URL: ")
    if choice == "1":
        print(webhooks.saferates_send(url, prompt("Content: "), username=prompt("Username (blank=default): ", required=False) or None))
    elif choice == "2":
        print(webhooks.saferates_edit(url, prompt("Message ID: "), content=prompt("New content: ")))
    elif choice == "3":
        print(webhooks.saferates_delete(url, prompt("Message ID: ")))
    pause()

def menu_roles(api):
    menu_header("Roles")
    roles = SaferatesRoles(api)
    print("1. Add role to self\n2. Remove role from self\n3. Back")
    choice = prompt("Select option: ")
    if choice == "1":
        print(roles.saferates_add_self_role(prompt("Guild ID: "), prompt("User ID: "), prompt("Role ID: ")))
    elif choice == "2":
        print(roles.saferates_remove_self_role(prompt("Guild ID: "), prompt("User ID: "), prompt("Role ID: ")))
    pause()

def menu_presence(api):
    menu_header("Presence / Nitro / Welcome / Reminders")
    presence = SaferatesPresence(api)
    nitro = SaferatesNitro(api)
    welcome = SaferatesWelcome(api)
    reminders = SaferatesReminders(api)
    print("1. Set custom status\n2. Set presence\n3. Check Nitro status\n4. Welcome new friend\n5. Schedule reminder\n6. Back")
    choice = prompt("Select option: ")
    if choice == "1":
        print(presence.saferates_set_custom_status(prompt("Status text: ")))
    elif choice == "2":
        print(presence.saferates_set_presence(
            status=prompt("online/idle/dnd/offline: "), activity_name=prompt("Activity name: ", required=False)
        ))
    elif choice == "3":
        print(nitro.saferates_check_nitro())
    elif choice == "4":
        print(welcome.saferates_welcome_new_friend(prompt("User ID: "), prompt("Welcome message: ")))
    elif choice == "5":
        print(reminders.saferates_remind_me(prompt("User ID: "), prompt("Message: "), int(prompt("Delay (seconds): "))))
    pause()

def menu_emojis(api):
    menu_header("Emojis")
    emojis = SaferatesEmojis(api)
    print("1. List emojis\n2. Upload emoji\n3. Delete emoji\n4. Back")
    choice = prompt("Select option: ")
    if choice == "1":
        print(emojis.saferates_list_emojis(prompt("Guild ID: ")))
    elif choice == "2":
        from saferates.utils import saferates_image_to_base64
        print(emojis.saferates_upload_emoji(
            prompt("Guild ID: "), prompt("Emoji name: "),
            saferates_image_to_base64(prompt("Path to image: "))
        ))
    elif choice == "3":
        print(emojis.saferates_delete_emoji(prompt("Guild ID: "), prompt("Emoji ID: ")))
    pause()

def menu_moderator(api):
    menu_header("Moderator Tools")
    mod = SaferatesModerator(api)
    print("1. Kick\n2. Ban\n3. Unban\n4. Timeout\n5. Back")
    choice = prompt("Select option: ")
    gid = prompt("Guild ID: ")
    uid = prompt("User ID: ")
    if choice == "1":
        print(mod.saferates_kick(gid, uid))
    elif choice == "2":
        print(mod.saferates_ban(gid, uid, int(prompt("Delete message days (0-7): ", required=False) or "0")))
    elif choice == "3":
        print(mod.saferates_unban(gid, uid))
    elif choice == "4":
        from datetime import datetime, timedelta
        mins = int(prompt("Minutes to timeout: "))
        until = (datetime.utcnow() + timedelta(minutes=mins)).isoformat() + "Z"
        print(mod.saferates_timeout(gid, uid, until))
    pause()

def menu_polls(api):
    menu_header("Polls")
    polls = SaferatesPolls(api)
    print("1. Create poll\n2. Back")
    choice = prompt("Select option: ")
    if choice == "1":
        channel = prompt("Channel ID: ")
        question = prompt("Poll question: ")
        opts = prompt("Poll emoji options (comma-separated, e.g. 🔴,🟢,🔵): ").split(",")
        print(polls.saferates_create_poll(channel, question, [o.strip() for o in opts if o.strip()]))
    pause()

def menu_voice(api):
    menu_header("Voice Tools")
    voice = SaferatesVoice(api)
    print("1. Move to voice channel\n2. Disconnect from voice\n3. Back")
    choice = prompt("Select option: ")
    gid = prompt("Guild ID: ")
    if choice == "1":
        print(voice.saferates_move_to_voice(gid, prompt("Channel ID: ")))
    elif choice == "2":
        print(voice.saferates_disconnect_voice(gid))
    pause()

def menu_events(api):
    menu_header("Events / Commands")
    from saferates.events import SaferatesEventSystem
    events = SaferatesEventSystem()
    commands = SaferatesCommands()
    print("1. List registered commands\n2. Add test command\n3. Trigger test command\n4. Back")
    choice = prompt("Select option: ")
    if choice == "1":
        print(commands.saferates_list_commands())
    elif choice == "2":
        def testcmd(): print("saferates test command triggered!")
        commands.saferates_add_command("test", testcmd)
        print("Added!")
    elif choice == "3":
        commands.saferates_run_command("test")
    pause()

def main():
    print("== saferates Discord Multitool ==")
    token = load_token()
    api = SaferatesAPI(token)
    while True:
        menu_header("Main Menu")
        print(
            "1. Account/Friends\n2. Guilds\n3. Channels\n4. Messaging\n5. Direct Messages/Anti-Spam"
            "\n6. Webhooks\n7. Roles\n8. Presence/Nitro/Welcome/Reminders\n9. Emojis"
            "\n10. Moderator\n11. Polls\n12. Voice\n13. Events/Commands\n14. Exit"
        )
        choice = prompt("Select option: ")
        if choice == "1":
            menu_account(api)
        elif choice == "2":
            menu_guilds(api)
        elif choice == "3":
            menu_channels(api)
        elif choice == "4":
            menu_messaging(api)
        elif choice == "5":
            menu_dm(api)
        elif choice == "6":
            menu_webhook()
        elif choice == "7":
            menu_roles(api)
        elif choice == "8":
            menu_presence(api)
        elif choice == "9":
            menu_emojis(api)
        elif choice == "10":
            menu_moderator(api)
        elif choice == "11":
            menu_polls(api)
        elif choice == "12":
            menu_voice(api)
        elif choice == "13":
            menu_events(api)
        elif choice == "14":
            print("Goodbye from saferates!")
            break

if __name__ == "__main__":
    main()