## Setup Automatic Startup on macOS (Login)

To have the `run.sh` script start automatically every time you log into your Mac, you can use a Launch Agent.

1.  **Copy the example plist file to your LaunchAgents directory:**

    If you have a `vibekanban.plist` template in this project:

    ```bash
    cp vibekanban.plist ~/Library/LaunchAgents/com.user.vibekanban.run.plist
    ```

    If you don't have a template, you'll need to create `~/Library/LaunchAgents/com.user.vibekanban.run.plist` with the following content (adjust the `Label` and `ProgramArguments` as needed):

    ```xml
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "[http://www.apple.com/DTDs/PropertyList-1.0.dtd](http://www.apple.com/DTDs/PropertyList-1.0.dtd)">
    <plist version="1.0">
    <dict>
        <key>Label</key>
        <string>com.user.vibekanban.run</string>
        <key>ProgramArguments</key>
        <array>
            <string>/Users/chisel/development/shahriarb/vibekanban/run.sh</string>
        </array>
        <key>RunAtLoad</key>
        <true/>
        </dict>
    </plist>
    ```

2.  **Edit the `.plist` file to set the correct path:**

    Open the file `~/Library/LaunchAgents/com.user.vibekanban.run.plist` in a text editor.
    **Crucially, find the `<string>/Users/chisel/development/shahriarb/vibekanban/run.sh</string>` line and ensure it points to the absolute path of _your_ `run.sh` script.** You can get the absolute path by navigating to the script in Finder, right-clicking, holding Option (⌥), and selecting "Copy 'run.sh' as Pathname".

3.  **Set the correct permissions for the `.plist` file:**

    ```bash
    chmod 644 ~/Library/LaunchAgents/com.user.vibekanban.run.plist
    ```

4.  **Load the Launch Agent:**

    This command tells `launchd` to recognize and start managing your script. It will run on the next login.

    ```bash
    launchctl load ~/Library/LaunchAgents/com.user.vibekanban.run.plist
    ```

5.  **(Optional) Start the agent immediately without logging out/in:**

    If you want to start the script right away without restarting:

    ```bash
    launchctl start com.user.vibekanban.run
    ```

---

**To stop and unload the agent later:**

```bash
launchctl unload ~/Library/LaunchAgents/com.user.vibekanban.run.plist
```

Then you can safely delete the ~/Library/LaunchAgents/com.user.vibekanban.run.plist file.
