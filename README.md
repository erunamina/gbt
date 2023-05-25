# File Backup Tool
I created this to back up specific (configurable) media files to online services.

# Work in progress
At this stage, new file identification and consolidation is working. Upload to Glacier is working as well.
I'd like to add other storage options at some point, but the originally-intended functionality is there. The next step 
is to add a command line interface so we can specify configs and such without running 
the entire process.

# Configuration
Configuration is automatically placed in ~/.gbtool/config.toml the first time the tool is run.
This can/should be edited for the directories and file types each user would like to back up.

After a backup, the latest backup timestamp is saved, so only files that have been created/modified
since the last backup will be changed for each execution. All files are consolidated into a zip file before upload.

