# TwitchPlaysEverything
Twitch Plays Chat bot with click support

using this: https://github.com/ReggX/pydirectinput_rgx

and: https://github.com/ourique-gus/pywitch - follow instructions there for click integration

had a problem with pywin32, had to downgrade it. pip install --upgrade pywin32==303

Uses Direct Input Windows API using SendInput and scan codes instead of the older and more unreliable virtual keys. This improves compatibility especially with DirectX games.

Can also support mouse movement and clicking with typed commands if you don't want to use the Twitch Extension.

main.py is an example program.

# work in progress
will document later
